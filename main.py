"""Entry point for ZigWheels scraper"""

import asyncio
import sys
from src.scraper import ZigWheelsProductionScraper
from src.scraper.exceptions import ScraperException


async def main():
    """Main execution"""
    try:
        scraper = ZigWheelsProductionScraper(  
            config_file="config/scraper_config.json",
            log_level="INFO"
        )
        
        await scraper.scrape_all()
        output_file = scraper.save_data()
        
        if output_file:
            print(f"\n✅ SUCCESS! Data saved to: {output_file}")
        
        return 0
    
    except ScraperException as e:
        print(f"\n❌ Scraper failed: {str(e)}")
        return 1
    
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 255


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
