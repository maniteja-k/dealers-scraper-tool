"""Enumerations used throughout the scraper"""

from enum import Enum


class ScraperStatus(Enum):
    """Scraper execution status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
