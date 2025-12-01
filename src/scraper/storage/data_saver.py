"""Save scraped data to various formats"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging
from ..models.dealer import DealerData
from ..exceptions import ScraperException


class DataSaver:
    """Handles saving data to files"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger('DataSaver')
    
    def save(
        self, 
        dealers: List[DealerData], 
        format_type: str = "excel",
        custom_filename: str = None
    ) -> Optional[str]:
        """Save dealer data to file"""
        if not dealers:
            self.logger.warning("No data to save!")
            return None
        
        try:
            # Validate filename to prevent path traversal
            if custom_filename:
                if ".." in custom_filename or "/" in custom_filename or "\\" in custom_filename:
                    raise ScraperException("Invalid filename: path traversal detected")
                base_name = custom_filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = f"zigwheels_dealers_{timestamp}"
            
            # Validate format type
            if format_type not in ["excel", "csv", "json"]:
                raise ScraperException(f"Invalid format type: {format_type}")
            
            df = pd.DataFrame([dealer.to_dict() for dealer in dealers])
            df = df.replace('', pd.NA)
            
            # Use proper file extensions
            ext = "xlsx" if format_type == "excel" else format_type
            output_file = self.output_dir / f"{base_name}.{ext}"
            
            if format_type == "excel":
                df.to_excel(output_file, index=False, engine='openpyxl')
            elif format_type == "csv":
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
            elif format_type == "json":
                df.to_json(output_file, orient='records', indent=2, force_ascii=False)
            
            self.logger.info(f"💾 Saved {len(df)} records to: {output_file}")
            return str(output_file)
        
        except Exception as e:
            self.logger.error(f"Failed to save data: {str(e)}")
            raise ScraperException(f"Data save failed: {str(e)}")
    
    def save_failed_scrapes(self, failed_scrapes: List[dict], filename: str = None):
        """Save failed scrape attempts"""
        if not failed_scrapes:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"failed_scrapes_{timestamp}.json"
        output_file = self.output_dir / filename
        
        with open(output_file, 'w') as f:
            json.dump(failed_scrapes, f, indent=2)
        
        self.logger.warning(f"⚠ Saved {len(failed_scrapes)} failed scrapes to: {output_file}")
