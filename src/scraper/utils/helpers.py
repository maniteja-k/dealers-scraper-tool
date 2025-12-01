"""Helper utility functions"""


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text or text in ['N/A', 'NA', 'n/a']:
        return ''
    return text.strip()


def normalize_location(location: str) -> str:
    """Normalize location name for URLs"""
    return location.lower().replace(' ', '-').replace('_', '-')


def format_phone(phone: str) -> str:
    """Format phone number"""
    if not phone:
        return ''
    # Remove all non-numeric characters
    digits = ''.join(filter(str.isdigit, phone))
    return digits
