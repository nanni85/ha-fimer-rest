"""DataUpdateCoordinator per FIMER UNO-DM con discriminazione guasto/notte."""
import base64
from datetime import timedelta
import logging
import asyncio
import aiohttp
import async_timeout

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

ZERO_ON_OFFLINE = {
    "Pgrid", "Pin", "Pin1", "Pin2",
    "Iin1", "Iin2", "Vin1", "Vin2",
    "Igrid", "Vgrid", "Fgrid", "Qgrid",
    "PacTogrid", "Fan1rpm", "efficiency"
}


class FimerDataCoordinator(DataUpdateCoordinator):
    """Coordina il polling dei dati dall'inverter."""

    def __init__(self, hass: HomeAssistant, entry_data: dict) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="FIMER UNO-DM",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = entry_data[CONF_HOST]
        creds = f"{entry_data[CONF_USERNAME]}:{entry_data[CONF_PASSWORD]}"
        self.auth_header = f"Basic {base64.b64encode(creds.encode('utf-8')).decode('utf-8')}"
        self.device_info_data = {}
        self._last_valid_data = {}
        self.is_connected = True

    def _is_daytime(self) -> bool:
        """Verifica se il sole è sorto tramite l'entità sun.sun di Home Assistant."""
        sun_state = self.hass.states.get("sun.sun")
        if sun_state:
            return sun_state.state == "above_horizon"
        return True  # Se sun.sun non è disponibile, assume giorno per sicurezza

    async def _async_update_data(self) -> dict:
        url = f"http://{self.host}/v1/livedata"
        headers = {
            "authorization": self.auth_header,
            "abb-debug": "abb-debug",
            "content-type": "application/json",
        }

        try:
            async with async_timeout.timeout(4):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            payload = await resp.json()
                            device_data = next((v for v in payload.values() if "points" in v and v["points"]), None)

                            if device_data:
                                self.is_connected = True
                                self.device_info_data = {
                                    "id": device_data.get("device_id", self.host),
                                    "model": device_data.get("device_model", "UNO-DM"),
                                }

                                data_dict = {p["name"]: p["value"] for p in device_data["points"]}
                                self._last_valid_data = data_dict.copy()
                                return data_dict

        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass

        # L'inverter non ha risposto
        self.is_connected = False

        # Se è GIORNO ed è irraggiungibile -> è un GUASTO o caduta di rete
        if self._is_daytime():
            _LOGGER.warning("Inverter FIMER non raggiungibile durante il giorno! Possibile anomalia.")
            raise UpdateFailed("Inverter non raggiungibile durante le ore di produzione.")

        # Se è NOTTE -> normale spegnimento dei pannelli: mantiene contatori e azzera istantanee
        if self._last_valid_data:
            offline_data = self._last_valid_data.copy()
            for key in ZERO_ON_OFFLINE:
                if key in offline_data:
                    offline_data[key] = 0.0
            offline_data["efficiency"] = 0.0
            return offline_data

        return {key: 0.0 for key in ZERO_ON_OFFLINE}