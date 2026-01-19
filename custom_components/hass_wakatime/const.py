"""Constants for the Wakatime integration."""

import hashlib

DOMAIN = "hass_wakatime"

# Configuration constants
CONF_API_URL = "api_url"
CONF_USER = "user"

# Default values
DEFAULT_API_URL = "https://wakatime.com/api/v1"
DEFAULT_USER = "current"


def generate_unique_id(api_url: str, user: str) -> str:
    """Generate a unique ID based on API URL and user."""
    # Use a hash of the API URL and user to create a unique identifier
    unique_string = f"{api_url}_{user}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:16]
