"""Sensori binari per FIMER UNO-DM."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FimerDataCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configura i sensori binari."""
    coordinator: FimerDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        FimerFanRunningBinarySensor(coordinator, entry),
        FimerAlarmBinarySensor(coordinator, entry),
        FimerConnectionBinarySensor(coordinator, entry),
    ]
    async_add_entities(entities)


class FimerConnectionBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Indica se l'inverter è connesso e raggiungibile via LAN."""

    def __init__(self, coordinator: FimerDataCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        device_id = coordinator.device_info_data.get("id", entry.entry_id)
        self._attr_unique_id = f"{device_id}_connectivity"
        self._attr_name = "Stato Connessione"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_has_entity_name = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"FIMER {coordinator.device_info_data.get('model', 'UNO-DM')}",
            manufacturer="FIMER / ABB",
            model=coordinator.device_info_data.get("model", "UNO-DM-PLUS"),
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_connected


class FimerFanRunningBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Indica se la ventola è in funzione."""

    def __init__(self, coordinator: FimerDataCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        device_id = coordinator.device_info_data.get("id", entry.entry_id)
        self._attr_unique_id = f"{device_id}_fan_running"
        self._attr_name = "Stato Ventola"
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_has_entity_name = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"FIMER {coordinator.device_info_data.get('model', 'UNO-DM')}",
            manufacturer="FIMER / ABB",
            model=coordinator.device_info_data.get("model", "UNO-DM-PLUS"),
        )

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        rpm = self.coordinator.data.get("Fan1rpm", 0)
        return float(rpm) > 0


class FimerAlarmBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Indica se ci sono allarmi o anomalie attive."""

    def __init__(self, coordinator: FimerDataCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        device_id = coordinator.device_info_data.get("id", entry.entry_id)
        self._attr_unique_id = f"{device_id}_alarm_state"
        self._attr_name = "Stato Allarme"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_has_entity_name = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"FIMER {coordinator.device_info_data.get('model', 'UNO-DM')}",
            manufacturer="FIMER / ABB",
            model=coordinator.device_info_data.get("model", "UNO-DM-PLUS"),
        )

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        alarm = self.coordinator.data.get("AlarmState", 0)
        return float(alarm) > 0