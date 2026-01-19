"""Config flow for Wakatime integration."""

from logging import getLogger
from typing import Any

from aiohttp.client import ClientSession
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import config_validation as cv

from .const import CONF_API_URL, CONF_USER, DEFAULT_API_URL, DEFAULT_USER, DOMAIN

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
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on the user
                await self.async_set_unique_id(f"wakatime_{user}")
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

        async with (
            ClientSession() as sess,
            sess.get(f"{api_url}/users/{user}/stats", headers=headers) as resp,
        ):
            resp.raise_for_status()
