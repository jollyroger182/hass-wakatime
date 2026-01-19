from logging import getLogger

from aiohttp.client import ClientSession
from custom_components.hass_wakatime import DOMAIN
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

LOGGER = getLogger(__name__)
PLATFORM_SCHEMA = vol.Schema(
    {
        "platform": DOMAIN,
        vol.Required("api_url", default="https://wakatime.com/api/v1"): vol.Url(),
        vol.Optional("api_key"): str,
        vol.Required("user", default="current"): str,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    LOGGER.debug("setting up sensor platform")
    add_entities([TotalCodingTimeSensor(config)], update_before_add=True)


class TotalCodingTimeSensor(SensorEntity):
    def __init__(self, config) -> None:
        LOGGER.debug("sensor created with config %r", config)
        self.__api_url = config["api_url"]
        self.__api_key = config["api_key"]
        self.__user = config["user"]
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
