"""Config flow per FIMER UNO-DM."""
import base64
import logging
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default="admin"): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


def get_auth_header(username: str, password: str) -> str:
    creds = f"{username}:{password}"
    encoded = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Verifica che i parametri inseriti riescano a contattare l'inverter."""
    host = data[CONF_HOST]
    auth_header = get_auth_header(data[CONF_USERNAME], data[CONF_PASSWORD])

    headers = {
        "authorization": auth_header,
        "abb-debug": "abb-debug",
        "content-type": "application/json",
    }
    url = f"http://{host}/v1/livedata"

    try:
        async with async_timeout.timeout(5):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 401:
                        raise InvalidAuth
                    if resp.status != 200:
                        raise CannotConnect

                    payload = await resp.json()
                    device_data = next((v for v in payload.values() if "device_id" in v), None)
                    device_id = device_data.get("device_id", host) if device_data else host
                    device_model = device_data.get("device_model", "UNO-DM") if device_data else "UNO-DM"

                    return {"title": f"FIMER {device_model} ({host})", "unique_id": device_id}

    except aiohttp.ClientError:
        raise CannotConnect


class FimerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestione configurazione guidata."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Errore inatteso")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Errore connessione di rete."""


class InvalidAuth(HomeAssistantError):
    """Errore autenticazione credenziali."""