"""Config flow for Wakatime integration."""

from logging import getLogger
from typing import Any

from aiohttp.client_exceptions import ClientError, ClientResponseError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_URL,
    CONF_USER,
    DEFAULT_API_URL,
    DEFAULT_USER,
    DOMAIN,
    generate_unique_id,
)

LOGGER = getLogger(__name__)


class WakatimeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wakatime."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the input by trying to connect to the API
            api_url = user_input[CONF_API_URL]
            api_key = user_input.get(CONF_API_KEY)
            user = user_input[CONF_USER]

            try:
                await self._test_connection(api_url, api_key, user)
            except ClientResponseError as err:
                LOGGER.error("HTTP error connecting to Wakatime API: %s", err)
                if err.status in (401, 403):
                    errors["base"] = "invalid_auth"
                elif err.status == 404:
                    errors["base"] = "user_not_found"
                else:
                    errors["base"] = "unknown"
            except ClientError as err:
                LOGGER.error("Connection error to Wakatime API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on the API URL and user
                unique_id = generate_unique_id(api_url, user)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Wakatime ({user})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default=DEFAULT_API_URL): cv.url,
                    vol.Optional(CONF_API_KEY): cv.string,
                    vol.Required(CONF_USER, default=DEFAULT_USER): cv.string,
                }
            ),
            errors=errors,
        )

    async def _test_connection(
        self, api_url: str, api_key: str | None, user: str
    ) -> None:
        """Test if we can connect to the Wakatime API."""
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        session = async_get_clientsession(self.hass)
        async with session.get(
            f"{api_url}/users/{user}/stats", headers=headers, timeout=10
        ) as resp:
            resp.raise_for_status()
