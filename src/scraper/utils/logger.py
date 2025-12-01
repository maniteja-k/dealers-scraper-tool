"""Logging configuration and setup"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ScraperLogger:
    """Centralized logging with file and console output"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"scraper_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('ZigWheelsScraper')
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get logger instance"""
        if name:
            return logging.getLogger(name)
        return self.logger
