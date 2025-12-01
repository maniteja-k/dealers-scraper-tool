"""ZigWheels Dealer Scraper Package"""

from .core.scraper import ZigWheelsProductionScraper
from .models.dealer import DealerData
from .models.enums import ScraperStatus

__version__ = "1.0.0"
__all__ = ["ZigWheelsProductionScraper", "DealerData", "ScraperStatus"]
