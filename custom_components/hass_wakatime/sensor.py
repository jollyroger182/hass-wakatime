from logging import getLogger

from aiohttp.client import ClientSession
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_API_URL, CONF_USER, DEFAULT_API_URL, DEFAULT_USER, DOMAIN

LOGGER = getLogger(__name__)
PLATFORM_SCHEMA = vol.Schema(
    {
        "platform": DOMAIN,
        vol.Required(CONF_API_URL, default=DEFAULT_API_URL): vol.Url(),
        vol.Optional(CONF_API_KEY): str,
        vol.Required(CONF_USER, default=DEFAULT_USER): str,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform from YAML configuration."""
    LOGGER.debug("setting up sensor platform")
    add_entities([TotalCodingTimeSensor(config)], update_before_add=True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform from a config entry."""
    LOGGER.debug("setting up sensor from config entry")
    add_entities([TotalCodingTimeSensor(entry.data)], update_before_add=True)


class TotalCodingTimeSensor(SensorEntity):
    """Sensor for total coding time from Wakatime."""

    def __init__(self, config: dict) -> None:
        """Initialize the sensor."""
        LOGGER.debug("sensor created with config %r", config)
        self.__api_url = config[CONF_API_URL]
        self.__api_key = config.get(CONF_API_KEY)
        self.__user = config[CONF_USER]
        self._state = None
        self._attr_unique_id = "wakatime_total_coding_time"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_name = "Total coding time"
        self._attr_has_entity_name = True
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS

    async def async_update(self) -> None:
        LOGGER.debug("updating time")
        headers = {}
        if self.__api_key:
            headers["Authorization"] = f"Bearer {self.__api_key}"

        async with (
            ClientSession() as sess,
            sess.get(
                f"{self.__api_url}/users/{self.__user}/stats", headers=headers
            ) as resp,
        ):
            data = await resp.json()
        LOGGER.debug("got response: %r", data)
        self._attr_native_value = data["data"]["total_seconds"]
