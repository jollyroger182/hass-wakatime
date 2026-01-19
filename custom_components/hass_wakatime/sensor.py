from logging import getLogger

from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientError
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_API_URL,
    CONF_USER,
    DEFAULT_API_URL,
    DEFAULT_USER,
    DOMAIN,
    generate_unique_id,
)

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
        # Create a unique ID based on the API URL and user to support multiple instances
        unique_id_hash = generate_unique_id(self.__api_url, self.__user)
        self._attr_unique_id = f"wakatime_total_coding_time_{unique_id_hash}"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_name = "Total coding time"
        self._attr_has_entity_name = True
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS

    async def async_update(self) -> None:
        """Update the sensor."""
        LOGGER.debug("updating time")
        headers = {}
        if self.__api_key:
            headers["Authorization"] = f"Bearer {self.__api_key}"

        try:
            async with (
                ClientSession() as sess,
                sess.get(
                    f"{self.__api_url}/users/{self.__user}/stats", headers=headers
                ) as resp,
            ):
                resp.raise_for_status()
                data = await resp.json()
            LOGGER.debug("got response: %r", data)
            self._attr_native_value = data["data"]["total_seconds"]
        except ClientError as err:
            LOGGER.error("Error fetching data from Wakatime API: %s", err)
            # Keep the previous value by not updating _attr_native_value
            return
        except (KeyError, ValueError) as err:
            LOGGER.error("Error parsing Wakatime API response: %s", err)
            # Keep the previous value by not updating _attr_native_value
            return
