from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity

LOGGER = getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    LOGGER.debug("setting up sensor platform")
    add_entities([LoadedSensor()])


class LoadedSensor(SensorEntity):
    def __init__(self) -> None:
        self._state = None
        self._attr_name = "Loaded"
        self._attr_has_entity_name = True
        self._attr_native_value = 1

    async def async_update(self) -> None:
        LOGGER.debug('sensor updated')
