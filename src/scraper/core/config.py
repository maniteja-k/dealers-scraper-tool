"""Configuration management"""

import json
from pathlib import Path
from typing import Dict, Optional
from ..exceptions import ConfigurationException
from ..utils.validators import validate_config


class ConfigManager:
    """Manages scraper configuration"""
    
    @staticmethod
    def load_config(config_file: Optional[str] = None) -> Dict:
        """Load and validate configuration"""
        if config_file:
            config_path = Path(config_file)
            # Prevent path traversal attacks
            if ".." in str(config_path):
                raise ConfigurationException("Invalid config file path: path traversal detected")
            
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                except json.JSONDecodeError as e:
                    raise ConfigurationException(f"Invalid JSON in config file: {str(e)}")
                except Exception as e:
                    raise ConfigurationException(f"Failed to read config file: {str(e)}")
            else:
                raise ConfigurationException(f"Config file not found: {config_file}")
        else:
            config = ConfigManager._default_config()
        
        # Validate
        is_valid, errors = validate_config(config)
        if not is_valid:
            raise ConfigurationException(f"Invalid configuration: {', '.join(errors)}")
        
        return config
    
    @staticmethod
    def _default_config() -> Dict:
        """Default production configuration"""
        return {
            "vehicle_types": {
                "cars": {
                    "base_url": "https://www.zigwheels.com/dealers",
                    "brands": ["maruti-suzuki", "tata", "kia", "toyota", "hyundai", "mahindra"]
                },
                "bikes": {
                    "base_url": "https://www.zigwheels.com/bikes/dealers",
                    "brands": ["hero", "honda", "bajaj", "tvs", "yamaha", "suzuki"]
                }
            },
            "locations": ["mumbai", "delhi", "bangalore", "hyderabad", "pune", "chennai"],
            "output_format": "excel",
            "headless": True,
            "timeout": 15000,
            "max_scroll": 5,
            "max_retries": 3,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "save_checkpoint_interval": 50,
            "validate_data": True,
            "skip_invalid": True,
            "location_discovery_phase": 2,
            "use_api_if_available": True
        }
