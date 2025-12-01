"""Custom exceptions for the scraper"""

from .custom_exceptions import (
    ScraperException,
    NetworkException,
    ParseException,
    RateLimitException,
    ConfigurationException,
    DataValidationException
)

__all__ = [
    "ScraperException",
    "NetworkException", 
    "ParseException",
    "RateLimitException",
    "ConfigurationException",
    "DataValidationException"
]
