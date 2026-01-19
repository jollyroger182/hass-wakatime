"""Display your Wakatime stats in Home Assistant."""

from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "hass_wakatime"

LOGGER = getLogger(__name__)


async def async_setup(hass: "HomeAssistant", config: "ConfigType"):
    LOGGER.debug("hass_wakatime loaded with config %r", (config))
    return True
