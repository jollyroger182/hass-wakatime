"""Display your Wakatime stats in Home Assistant."""

from logging import getLogger

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

__all__ = ["DOMAIN"]

LOGGER = getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Wakatime component from YAML configuration."""
    LOGGER.debug("hass_wakatime loaded with config %r", config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wakatime from a config entry."""
    LOGGER.debug("Setting up Wakatime config entry: %s", entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.debug("Unloading Wakatime config entry: %s", entry.data)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
