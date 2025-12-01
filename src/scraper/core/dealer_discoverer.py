"""Dealer discovery from Zigwheels for efficient batch querying"""

import asyncio
import logging
import json
import httpx
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class DealerDiscoverer:
    """Discovers dealers efficiently using city enumeration"""
    
    # Cities JSON (get from CityDiscoverer output)
    CITIES_JSON_URL = "https://www.zigcdn.com/js/city_json.js?version=147.7"
    
    # Dealer page template
    DEALER_PAGE_TEMPLATE = "https://www.zigwheels.com/dealers/{brand}/{city}"
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger('DealerDiscoverer')
        self.discovered_dealers: List[Dict] = []
        self.cities_data: List[Dict] = []
        
    def get_dealer_page_url(self, brand: str, city: str) -> str:
        """Get the dealer page URL for a brand and city"""
        # Format: brand-slug/City (with proper URL formatting)
        city_slug = city.replace(' ', '-').replace(',', '')
        return self.DEALER_PAGE_TEMPLATE.format(brand=brand, city=city_slug)
    
    async def get_dealer_urls_to_scrape(
        self,
        brand: str,
        cities: List[str] = None
    ) -> List[str]:
        """
        Get list of dealer page URLs to scrape for a brand.
        
        Args:
            brand: Brand slug (e.g., 'maruti-suzuki')
            cities: List of city names (if None, uses all cities)
            
        Returns:
            List of dealer page URLs
        """
        self.logger.info(f"Generating dealer URLs for {brand}")
        
        try:
            # Load cities if not provided
            if not cities:
                cities = await self._load_cities()
            
            if not cities:
                self.logger.error("No cities available")
                return []
            
            # Generate URLs for all city combinations
            urls = []
            for city in cities:
                url = self.get_dealer_page_url(brand, city)
                urls.append(url)
            
            self.logger.info(f"Generated {len(urls)} dealer page URLs for {brand}")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error generating dealer URLs: {str(e)}")
            return []
    

    
    async def _load_cities(self) -> List[str]:
        """Load cities from JSON API or saved file"""
        try:
            # Try to load from saved file first
            cities_file = self._find_latest_cities_file()
            if cities_file:
                self.logger.info(f"Loading cities from {cities_file}")
                with open(cities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('cities', [])
            
            # Fetch from API
            self.logger.info("Fetching cities from API...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.CITIES_JSON_URL)
                response.raise_for_status()
                
                cities_data = response.json()
                if isinstance(cities_data, list):
                    cities = sorted(list(set([
                        c.get('value', '') for c in cities_data if c.get('value')
                    ])))
                    self.cities_data = cities_data
                    return cities
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error loading cities: {str(e)}")
            return []
    
    def _find_latest_cities_file(self) -> Optional[str]:
        """Find the latest saved cities file"""
        try:
            output_dir = Path("output")
            cities_files = sorted(output_dir.glob("cities_*.json"))
            if cities_files:
                return str(cities_files[-1])
        except Exception as e:
            self.logger.debug(f"Error finding cities file: {str(e)}")
        
        return None
    
    def _save_discovered_dealers(self, brand: str):
        """Save discovered dealers to JSON file"""
        try:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"dealers_{brand}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'brand': brand,
                'total_dealers': len(self.discovered_dealers),
                'dealers': self.discovered_dealers
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✓ Dealers saved to: {output_file}")
            return str(output_file)
        
        except Exception as e:
            self.logger.error(f"Error saving dealers: {str(e)}")
            return None
