"""City discovery from Zigwheels static JSON API"""

import asyncio
import logging
import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import httpx


class CityDiscoverer:
    """Discovers all cities from Zigwheels static JSON API"""
    
    CITIES_JSON_URL = "https://www.zigcdn.com/js/city_json.js?version=147.7"
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger('CityDiscoverer')
        self.discovered_cities: List[Dict] = []
        
    async def discover_all_cities(self, page=None) -> List[str]:
        """
        Discover all cities by fetching the Zigwheels static JSON file.
        This is much faster and more reliable than DOM scraping.
        
        Returns:
            List of city names
        """
        self.logger.info("Starting city discovery from static JSON API...")
        self.discovered_cities.clear()
        
        try:
            # Fetch JSON from CDN
            cities_data = await self._fetch_cities_json()
            
            if not cities_data:
                self.logger.error("Failed to fetch cities JSON")
                return []
            
            self.logger.info(f"✓ Fetched {len(cities_data)} cities from API")
            self.discovered_cities = cities_data
            
            # Extract just the city names
            cities_list = sorted(list(set([city.get('value', '') for city in cities_data if city.get('value')])))
            
            self.logger.info(f"✓ Discovery complete! Total unique cities: {len(cities_list)}")
            self._save_discovered_cities(cities_data, cities_list)
            
            return cities_list
        
        except Exception as e:
            self.logger.error(f"Error discovering cities: {str(e)}")
            return []
    
    async def _fetch_cities_json(self) -> List[Dict]:
        """Fetch cities JSON from Zigwheels CDN"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.CITIES_JSON_URL)
                response.raise_for_status()
                
                # The response is JSON array
                cities_data = response.json()
                
                if not isinstance(cities_data, list):
                    self.logger.error(f"Unexpected response format: {type(cities_data)}")
                    return []
                
                self.logger.debug(f"Successfully fetched {len(cities_data)} cities")
                return cities_data
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error fetching cities JSON: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching cities JSON: {str(e)}")
            return []
    
    def _save_discovered_cities(self, cities_data: List[Dict], cities_list: List[str]):
        """Save discovered cities to JSON file"""
        try:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"cities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'Zigwheels Static JSON API',
                'source_url': self.CITIES_JSON_URL,
                'total_cities': len(cities_list),
                'cities': sorted(cities_list),
                'cities_data': cities_data  # Full data with IDs and codes
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✓ Cities saved to: {output_file}")
            return str(output_file)
        
        except Exception as e:
            self.logger.error(f"Error saving cities: {str(e)}")
            return None
    
    def load_cities_from_file(self, filepath: str = None) -> List[str]:
        """Load previously discovered cities from file"""
        try:
            if filepath:
                file_path = Path(filepath)
            else:
                # Find latest cities file
                output_dir = Path("output")
                cities_files = list(output_dir.glob("cities_*.json"))
                if not cities_files:
                    self.logger.warning("No saved cities files found")
                    return []
                file_path = sorted(cities_files)[-1]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities = data.get('cities', [])
                self.logger.info(f"Loaded {len(cities)} cities from {file_path}")
                return cities
        
        except Exception as e:
            self.logger.error(f"Error loading cities: {str(e)}")
            return []
