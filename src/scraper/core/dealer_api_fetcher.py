"""Fetch dealers from Zigwheels via direct page navigation"""

import asyncio
import logging
from typing import List, Dict

class DealerAPIFetcher:
    """Fetch dealers by navigating to dealer pages and extracting from DOM"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger('DealerAPIFetcher')
    
    async def get_dealers(self, page, brand: str, city: str, vehicle_type: str = "cars") -> List[Dict]:
        """
        Fetch dealers for brand in city by navigating to URL
        
        Args:
            page: Playwright page object
            brand: Car brand (bmw, audi, maruti-suzuki, etc.)
            city: City name (exact as from city JSON)
            vehicle_type: Vehicle type (cars, bikes, etc.)
        
        Returns:
            List of dealer dictionaries with details
        """
        try:
            # Format URL: /dealers/{brand}/{city}
            # Brand and city should be lowercased and hyphenated
            brand_slug = brand.lower().strip()
            city_slug = city.lower().strip().replace(' ', '-').replace(',', '')
            
            url = f"https://www.zigwheels.com/dealers/{brand_slug}/{city_slug}"
            
            self.logger.debug(f"Fetching {brand} dealers in {city}...")
            
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1)  # Wait for JS to render
            
            # Extract dealers from page
            dealers = await self._extract_dealers_from_page(page, brand, city)
            
            if dealers:
                self.logger.info(f"  ✓ {city}: Found {len(dealers)} dealers")
            else:
                self.logger.debug(f"  No dealers found for {brand} in {city}")
            
            return dealers
        
        except Exception as e:
            self.logger.debug(f"Error fetching dealers for {brand} in {city}: {e}")
            return []
    
    async def _extract_dealers_from_page(self, page, brand: str, city: str) -> List[Dict]:
        """Extract dealers from current page using deal-crd class selector"""
        try:
            dealers = await page.evaluate(r"""() => {
                const results = [];
                const seenNames = new Set();
                
                // Target dealer card structure with deal-crd class
                const dealerCards = document.querySelectorAll('[class*="deal-crd"]');
                
                dealerCards.forEach(card => {
                    try {
                        // Extract dealer name from h3
                        const nameElem = card.querySelector('h3');
                        const dealerName = nameElem ? nameElem.innerText.trim() : '';
                        
                        if (!dealerName || dealerName.length < 2) return;
                        
                        // Extract address from paragraphs
                        let address = '';
                        const paragraphs = card.querySelectorAll('p');
                        if (paragraphs.length > 0) {
                            address = paragraphs[0].innerText.trim();
                        }
                        
                        // Extract email
                        let email = '';
                        const cardText = card.innerText || card.textContent || '';
                        const emailMatch = cardText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
                        if (emailMatch) {
                            email = emailMatch[0];
                        }
                        
                        // Extract phone
                        let phone = '';
                        const telLink = card.querySelector('a[href^="tel:"]');
                        if (telLink) {
                            phone = telLink.innerText.trim();
                        } else {
                            const phoneMatch = cardText.match(/[0-9]{10,}/);
                            if (phoneMatch) {
                                phone = phoneMatch[0];
                            }
                        }
                        
                        const key = dealerName.toLowerCase().trim();
                        if (!seenNames.has(key) && dealerName.length > 3) {
                            results.push({
                                dealer_name: dealerName,
                                address: address,
                                email: email,
                                phone: phone
                            });
                            seenNames.add(key);
                        }
                    } catch (e) {
                        console.debug('Error processing card:', e);
                    }
                });
                
                return results;
            }""")
            
            return dealers if isinstance(dealers, list) else []
        
        except Exception as e:
            self.logger.debug(f"Error extracting dealers: {e}")
            return []
    
    async def get_dealers_batch(self, page, brand: str, cities: List[str], vehicle_type: str = "cars") -> Dict[str, List[Dict]]:
        """
        Fetch dealers for brand across multiple cities
        
        Args:
            page: Playwright page object
            brand: Car brand
            cities: List of city names
            vehicle_type: Vehicle type
        
        Returns:
            Dictionary mapping city -> dealers list
        """
        results = {}
        total_cities = len(cities)
        
        for idx, city in enumerate(cities):
            self.logger.info(f"[{idx+1}/{total_cities}] Fetching {brand} dealers in {city}...")
            
            dealers = await self.get_dealers(page, brand, city, vehicle_type)
            if dealers:
                results[city] = dealers
            
            # Rate limiting - avoid hammering site
            if idx < total_cities - 1:
                await asyncio.sleep(1)
        
        return results
