"""Browser management and initialization"""

from playwright.async_api import async_playwright, Browser, BrowserContext
from ..exceptions import NetworkException
import logging


class BrowserManager:
    """Manages Playwright browser lifecycle"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger('BrowserManager')
    
    async def launch_browser(self, playwright) -> Browser:
        """Launch browser with error handling"""
        try:
            self.logger.info("Launching browser...")
            browser = await playwright.chromium.launch(
                headless=self.config['headless'],
                args=['--disable-blink-features=AutomationControlled']
            )
            self.logger.info("✓ Browser launched successfully")
            return browser
        except Exception as e:
            raise NetworkException(f"Failed to launch browser: {str(e)}")
    
    async def create_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with anti-detection"""
        try:
            context = await browser.new_context(
                user_agent=self.config.get('user_agent'),
                viewport={'width': 1920, 'height': 1080},
                locale='en-IN',
                timezone_id='Asia/Kolkata'
            )
            return context
        except Exception as e:
            raise NetworkException(f"Failed to create browser context: {str(e)}")
