"""Dealer data model with validation"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Tuple, List, Dict


@dataclass
class DealerData:
    """Structured dealer information with validation"""
    vehicle_type: str
    brand: str
    location: str
    dealer_name: str
    address: str = ""
    phone: str = ""
    email: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""
    dealer_code: str = ""
    scraped_at: str = ""
    source_url: str = ""
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        self.scraped_at = self.scraped_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._clean_fields()
    
    def _clean_fields(self):
        """Clean and normalize field values"""
        for field in ['dealer_name', 'address', 'phone', 'email', 'city', 'state', 'pincode']:
            value = getattr(self, field, '')
            if value in ['N/A', 'NA', 'n/a', None]:
                setattr(self, field, '')
            elif isinstance(value, str):
                setattr(self, field, value.strip())
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate dealer data quality"""
        errors = []
        
        if not self.dealer_name or self.dealer_name == '':
            errors.append("Missing dealer name")
        
        # At least one of address, city, or location should exist
        if not self.address and not self.city and not self.location:
            errors.append("Missing address, city, and location")
        
        if len(self.dealer_name) < 2:
            errors.append(f"Dealer name too short: '{self.dealer_name}'")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DataFrame"""
        return asdict(self)
