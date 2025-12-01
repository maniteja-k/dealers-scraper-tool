"""Custom exception classes for error handling"""

from typing import Dict, Optional


class ScraperException(Exception):
    """Base exception for scraper errors"""
    def __init__(self, message: str, url: str = None, context: Dict = None):
        self.message = message
        self.url = url
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        base = f"{self.message}"
        if self.url:
            base += f" (URL: {self.url})"
        if self.context:
            base += f" | Context: {self.context}"
        return base


class NetworkException(ScraperException):
    """Network-related errors (timeouts, connection failures)"""
    pass


class ParseException(ScraperException):
    """HTML parsing and data extraction errors"""
    pass


class RateLimitException(ScraperException):
    """Rate limiting or anti-bot detection"""
    pass


class ConfigurationException(ScraperException):
    """Configuration file or setup errors"""
    pass


class DataValidationException(ScraperException):
    """Data quality or validation errors"""
    pass
