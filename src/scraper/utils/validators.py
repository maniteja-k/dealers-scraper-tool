"""Data validation functions"""

from typing import Dict, List, Tuple
from ..exceptions import ConfigurationException, DataValidationException


def validate_config(config: Dict) -> Tuple[bool, List[str]]:
    """Validate scraper configuration"""
    errors = []
    
    required_keys = ['vehicle_types', 'output_format', 'timeout']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required config key: {key}")
    
    if config.get('timeout', 0) <= 0:
        errors.append("Timeout must be positive")
    
    if config.get('output_format') not in ['excel', 'csv', 'json']:
        errors.append("Invalid output format")
    
    return (len(errors) == 0, errors)


def validate_dealer_data(dealer_dict: Dict) -> Tuple[bool, List[str]]:
    """Validate dealer data dictionary"""
    errors = []
    
    required_fields = ['dealer_name', 'vehicle_type', 'brand', 'location']
    for field in required_fields:
        if field not in dealer_dict or not dealer_dict[field]:
            errors.append(f"Missing required field: {field}")
    
    return (len(errors) == 0, errors)
