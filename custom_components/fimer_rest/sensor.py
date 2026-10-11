"""Sensori per FIMER UNO-DM."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FimerDataCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    # Potenze e Produzione Giornaliera / Totale
    SensorEntityDescription(
        key="Pgrid",
        name="Potenza AC Attuale",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Pin",
        name="Potenza DC Totale",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Ppeak",
        name="Picco Potenza Oggi",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="efficiency",
        name="Efficienza Conversione",
        native_unit_of_measurement="%",
        icon="mdi:percent",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="E0_runtime",
        name="Produzione Oggi",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="ETotal",
        name="Produzione Totale",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # Statistiche di Periodo
    SensorEntityDescription(
        key="E0_7D",
        name="Produzione Ultimi 7 Giorni",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="E0_30D",
        name="Produzione Ultimi 30 Giorni",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # Stringhe MPPT
    SensorEntityDescription(
        key="Vin1",
        name="Tensione Stringa 1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Iin1",
        name="Corrente Stringa 1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Vin2",
        name="Tensione Stringa 2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Iin2",
        name="Corrente Stringa 2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Rete Elettrica AC
    SensorEntityDescription(
        key="Vgrid",
        name="Tensione di Rete",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Fgrid",
        name="Frequenza di Rete",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Diagnostica, Temperature, Ventola e Isolamento
    SensorEntityDescription(
        key="TempInv",
        name="Temperatura Inverter",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Riso",
        name="Resistenza di Isolamento",
        native_unit_of_measurement="MΩ",
        icon="mdi:shield-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Fan1rpm",
        name="Velocità Ventola",
        native_unit_of_measurement="RPM",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configura i sensori FIMER."""
    coordinator: FimerDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        FimerSensor(coordinator, desc, entry)
        for desc in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class FimerSensor(CoordinatorEntity, SensorEntity):
    """Rappresentazione di un sensore FIMER."""

    def __init__(
        self,
        coordinator: FimerDataCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        device_id = coordinator.device_info_data.get("id", entry.entry_id)
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_has_entity_name = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"FIMER {coordinator.device_info_data.get('model', 'UNO-DM')}",
            manufacturer="FIMER / ABB",
            model=coordinator.device_info_data.get("model", "UNO-DM-PLUS"),
        )

    @property
    def native_value(self):
        """Calcola o restituisce il valore formattato."""
        if not self.coordinator.data:
            return None

        # Calcolo efficienza percentuale: (Pgrid / Pin) * 100
        if self.entity_description.key == "efficiency":
            pgrid = self.coordinator.data.get("Pgrid")
            pin = self.coordinator.data.get("Pin")
            if pin is not None and pin > 10 and pgrid is not None and pgrid > 0:
                eff = (pgrid / pin) * 100.0
                return round(min(eff, 100.0), 1)
            return 0.0

        raw_val = self.coordinator.data.get(self.entity_description.key)
        if raw_val is None:
            return None

        # Conversione dei contatori da Wh a kWh
        if self.entity_description.key in ("E0_runtime", "ETotal", "E0_7D", "E0_30D"):
            return round(raw_val / 1000.0, 2)

        return round(raw_val, 2)