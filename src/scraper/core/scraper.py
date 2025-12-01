"""Main scraper orchestration - imports from modular components"""

import asyncio
import logging
import random
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..models.dealer import DealerData
from ..models.enums import ScraperStatus
from ..exceptions import NetworkException, ParseException, ScraperException
from ..core.config import ConfigManager
from ..core.browser import BrowserManager
# from ..core.api_discoverer import APIDiscoverer  # Not needed - using main scraping path
# from ..core.location_traverser import LocationTraverser  # Not needed - using main scraping path
from ..core.dealer_api_fetcher import DealerAPIFetcher
from ..extractors.dealer_extractor import DealerExtractor
# from ..extractors.location_extractor import LocationExtractor  # Not needed - using main scraping path
from ..storage.data_saver import DataSaver
from ..utils.logger import ScraperLogger


class ZigWheelsProductionScraper:
    """Production-ready ZigWheels dealer scraper - Main orchestrator"""
    
    def __init__(self, config_file: str = None, log_level: str = "INFO"):
        # Initialize logging
        self.logger_manager = ScraperLogger(log_level=log_level)
        self.logger = self.logger_manager.get_logger()
        
        # Load configuration
        self.config = ConfigManager.load_config(config_file)
        
        # Initialize components
        self.browser_manager = BrowserManager(self.config)
        self.dealer_extractor = DealerExtractor()
        # self.location_extractor = LocationExtractor(self.config)  # Not needed
        # self.api_discoverer = APIDiscoverer()  # Not needed
        # self.location_traverser = LocationTraverser(self.config)  # Not needed
        self.dealer_api_fetcher = DealerAPIFetcher(self.config)
        self.data_saver = DataSaver()
        
        # State
        self.dealers_data: List[DealerData] = []
        self.failed_scrapes: List[Dict] = []
        self.status = ScraperStatus.IDLE
        self.stats = {
            'total_attempts': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'invalid_data': 0,
            'retries': 0
        }
        
        Path("checkpoints").mkdir(exist_ok=True)
    
    async def _natural_delay(self, min_seconds: float = 2, max_seconds: float = 8):
        """Add natural random delay to avoid detection as bot"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    # Commented out - not needed for main scraping path
    # async def _get_locations_for_brand(self, page, brand: str) -> List[str]:
    
    async def scrape_all(self):
        """Main orchestration"""
        self.status = ScraperStatus.RUNNING
        self.logger.info("="*80)
        self.logger.info("STARTING ZIGWHEELS DEALER SCRAPER")
        self.logger.info("="*80)
        
        try:
            async with async_playwright() as p:
                browser = await self.browser_manager.launch_browser(p)
                
                try:
                    context = await self.browser_manager.create_context(browser)
                    page = await context.new_page()
                    
                    for vehicle_type, vehicle_config in self.config['vehicle_types'].items():
                        await self._scrape_vehicle_type(page, vehicle_type, vehicle_config)
                    
                    self.status = ScraperStatus.COMPLETED
                    self.logger.info("✅ Scraping completed successfully")
                
                finally:
                    await context.close()
                    await browser.close()
                    self._print_summary()
        
        except NetworkException as e:
            self.logger.error(f"Network error: {str(e)}", exc_info=True)
            self.status = ScraperStatus.FAILED
            raise
        except ScraperException as e:
            self.logger.error(f"Scraper error: {str(e)}")
            self.status = ScraperStatus.FAILED
            raise
        except Exception as e:
            self.logger.critical(f"Fatal error: {str(e)}", exc_info=True)
            self.status = ScraperStatus.FAILED
            raise ScraperException(f"Scraper failed: {str(e)}")
    
    async def _scrape_vehicle_type(self, page, vehicle_type: str, vehicle_config: Dict):
        """Scrape all brands for vehicle type"""
        self.logger.info(f"\n{'='*80}\n🚗 VEHICLE TYPE: {vehicle_type.upper()}\n{'='*80}")
        
        brands_list = vehicle_config.get('brands', [])
        
        for brand_idx, brand_config in enumerate(brands_list):
            # Natural delay between brand scrapes
            if brand_idx > 0:
                await self._natural_delay(3, 8)
            
            # Handle both old format (string) and new format (dict)
            if isinstance(brand_config, str):
                brand_name = brand_config
                locations = None
            else:
                brand_name = brand_config.get('name')
                locations = brand_config.get('locations')
            
            try:
                await self._scrape_brand(page, vehicle_type, brand_name, vehicle_config['base_url'], locations)
            except Exception as e:
                self.logger.error(f"Failed brand {brand_name}: {str(e)}")
                self.failed_scrapes.append({
                    'vehicle_type': vehicle_type,
                    'brand': brand_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    async def _scrape_brand_via_api(self, page, brand: str, vehicle_type: str, locations: List[str]):
        """Scrape dealers for brand across locations"""
        self.logger.info(f"→ Fetching {brand} dealers ({len(locations)} locations)...")
        
        dealers_by_city = await self.dealer_api_fetcher.get_dealers_batch(
            page=page,
            brand=brand,
            cities=locations,
            vehicle_type=vehicle_type
        )
        
        total_dealers = 0
        for city, dealers in dealers_by_city.items():
            if not dealers:
                continue
            
            for dealer_dict in dealers:
                try:
                    # Convert API response to DealerData model
                    dealer = DealerData(
                        vehicle_type=vehicle_type,
                        brand=brand,
                        location=city,
                        dealer_name=dealer_dict.get('dealer_name', ''),
                        phone=dealer_dict.get('phone', ''),
                        address=dealer_dict.get('address', ''),
                        email=dealer_dict.get('email', ''),
                        source_url=dealer_dict.get('url', '')
                    )
                    
                    is_valid, errors = dealer.is_valid()
                    if is_valid or not self.config.get('validate_data'):
                        self.dealers_data.append(dealer)
                        total_dealers += 1
                    else:
                        self.stats['invalid_data'] += 1
                        if self.config.get('validate_data'):
                            self.logger.debug(f"Invalid dealer: {errors}")
                
                except Exception as e:
                    self.logger.debug(f"Error processing dealer: {e}")
                    self.stats['invalid_data'] += 1
        
        self.stats['successful_scrapes'] += total_dealers
        self.logger.info(f"  ✓ API: Found {total_dealers} dealers for {brand}")
        return total_dealers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((NetworkException, PlaywrightTimeout))
    )
    async def _scrape_brand(self, page, vehicle_type: str, brand: str, base_url: str, config_locations=None):
        """Scrape all locations for brand"""
        self.logger.info(f"\n→ Brand: {brand}")
        
        # Determine which locations to scrape
        if config_locations == "all":
            # Fetch cities from JSON API
            self.logger.info(f"  → Fetching all Indian cities from ZigWheels API...")
            from .city_discoverer import CityDiscoverer
            city_discoverer = CityDiscoverer()
            
            # Try to load cached cities first
            locations = city_discoverer.load_cities_from_file()
            if not locations:
                # Fetch fresh cities
                locations = await city_discoverer.discover_all_cities()
            
            if not locations:
                self.logger.error(f"Failed to get cities for {brand}")
                return
            
            self.logger.info(f"  → Found {len(locations)} cities, scraping {brand} dealers...")
            await self._scrape_brand_via_api(page, brand, vehicle_type, locations)
            
        elif isinstance(config_locations, list):
            # Use only specified locations
            locations = config_locations
            self.logger.info(f"  → Using {len(locations)} configured locations")
            await self._scrape_brand_via_api(page, brand, vehicle_type, locations)
        
        else:
            # Default: use all cities
            self.logger.info(f"  → Fetching all cities for {brand}...")
            from .city_discoverer import CityDiscoverer
            city_discoverer = CityDiscoverer()
            locations = city_discoverer.load_cities_from_file()
            if not locations:
                locations = await city_discoverer.discover_all_cities()
            
            if locations:
                await self._scrape_brand_via_api(page, brand, vehicle_type, locations)
    
    async def _scrape_location(self, page, vehicle_type: str, brand: str, location: str, location_url: str):
        """Scrape dealers for location"""
        self.logger.info(f"    → {location}")
        
        try:
            await page.goto(location_url, wait_until="networkidle", timeout=self.config['timeout'])
            
            # Natural delay to let page fully load and simulate human behavior
            await self._natural_delay(1, 4)
            
            await self._scroll_page(page)
            
            dealers = await self.dealer_extractor.extract_dealers(
                page, vehicle_type, brand, location, location_url
            )
            
            if not dealers:
                self.logger.debug(f"No dealers found for {brand} in {location}")
                return
            
            valid_count = 0
            for dealer in dealers:
                is_valid, errors = dealer.is_valid()
                if is_valid or not self.config.get('validate_data'):
                    self.dealers_data.append(dealer)
                    valid_count += 1
                else:
                    self.stats['invalid_data'] += 1
                    self.logger.debug(f"Invalid dealer: {errors}")
            
            self.stats['successful_scrapes'] += valid_count
            self.logger.info(f"      ✓ Extracted {valid_count} dealers")
        
        except NetworkException as e:
            self.stats['failed_scrapes'] += 1
            self.logger.warning(f"Network error during scrape: {str(e)}")
            raise
        except Exception as e:
            self.stats['failed_scrapes'] += 1
            self.logger.error(f"Failed location scrape: {str(e)}")
    
    async def _scroll_page(self, page):
        """Scroll to load dynamic content with edge case handling"""
        try:
            max_scrolls = self.config.get('max_scroll', 5)
            for scroll_idx in range(max_scrolls):
                try:
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1500)
                except Exception as e:
                    self.logger.debug(f"Scroll {scroll_idx} failed: {str(e)}, continuing...")
                    continue
        except Exception as e:
            self.logger.warning(f"Page scroll failed: {str(e)}, continuing with extraction...")
    
    def save_data(self, custom_filename: str = None) -> str:
        """Save scraped data"""
        output_file = self.data_saver.save(
            self.dealers_data,
            format_type=self.config.get('output_format', 'excel'),
            custom_filename=custom_filename
        )
        
        if self.failed_scrapes:
            self.data_saver.save_failed_scrapes(self.failed_scrapes)
        
        return output_file
    
    def _print_summary(self):
        """Print execution summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("📊 FINAL SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Total Dealers: {len(self.dealers_data)}")
        self.logger.info(f"Successful: {self.stats['successful_scrapes']}")
        self.logger.info(f"Failed: {self.stats['failed_scrapes']}")
        self.logger.info("="*80 + "\n")
