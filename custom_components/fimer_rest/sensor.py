"""Sensori per FIMER UNO-DM con supporto stringhe avanzato, isolamento, temperature, contatori energia e allarmi dinamici."""
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

# Mappatura stati ciclo-vita globali dell'inverter
GLOBAL_STATE_MAP = {
    0: "Inizializzazione",
    1: "Controllo Isolamento (Alba)",
    2: "Attesa Irraggiamento Solare",
    3: "Controllo Rete Elettrica",
    4: "Sincronizzazione Rete",
    5: "In Produzione (Run)",
    6: "In Produzione (Run)",
    7: "Derating Potenza",
    8: "Protezione Termica",
    9: "Standby Notturno (Sleep)",
    10: "Bloccato per Allarme",
}

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    # Potenze Istantanee e Rendimento
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
        key="Pin1",
        name="Potenza Stringa 1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Pin2",
        name="Potenza Stringa 2",
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

    # Statistiche di Produzione (Lifetime, Anno Corrente, Oggi e Periodi)
    SensorEntityDescription(
        key="ETotal",
        name="Produzione Totale (Lifetime)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="E0_1Y",
        name="Produzione Anno Corrente",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="E0_runtime",
        name="Produzione Oggi",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
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

    # Dati Canali MPPT (Tensioni e Correnti)
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

    # Diagnostica, Isolamento e Temperature
    SensorEntityDescription(
        key="TempInv",
        name="Temperatura Inverter",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="TempBst",
        name="Temperatura Stadio Booster",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Temp1",
        name="Temperatura Sistema",
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
        key="Ileak",
        name="Corrente Dispersione a Terra",
        native_unit_of_measurement="mA",
        icon="mdi:flash-alert",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Fan1rpm",
        name="Velocità Ventola",
        native_unit_of_measurement="RPM",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Diagnostica Operativa e Allarmi
    SensorEntityDescription(
        key="GlobalState",
        name="Stato Operativo Inverter",
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="AlarmState",
        name="Stato Allarme Inverter",
        icon="mdi:shield-alert-outline",
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

        # 1. Calcolo Efficienza (%)
        if self.entity_description.key == "efficiency":
            pgrid = self.coordinator.data.get("Pgrid")
            pin = self.coordinator.data.get("Pin")
            if pin is not None and pin > 10 and pgrid is not None and pgrid > 0:
                return round(min((pgrid / pin) * 100.0, 100.0), 1)
            return 0.0

        # 2. Potenza Stringa 1 (W)
        if self.entity_description.key == "Pin1":
            p1 = self.coordinator.data.get("Pin1")
            if p1 is not None:
                return round(float(p1), 1)
            v1 = self.coordinator.data.get("Vin1", 0)
            i1 = self.coordinator.data.get("Iin1", 0)
            return round(float(v1) * float(i1), 1)

        # 3. Potenza Stringa 2 (W)
        if self.entity_description.key == "Pin2":
            p2 = self.coordinator.data.get("Pin2")
            if p2 is not None:
                return round(float(p2), 1)
            v2 = self.coordinator.data.get("Vin2", 0)
            i2 = self.coordinator.data.get("Iin2", 0)
            return round(float(v2) * float(i2), 1)

        # 4. Corrente di Dispersione (mA con normalizzazione microampere)
        if self.entity_description.key == "Ileak":
            val = self.coordinator.data.get("Ileak") or self.coordinator.data.get("IleakDC")
            if val is not None:
                f_val = float(val)
                if f_val > 100:
                    return round(f_val / 1000.0, 1)
                return round(f_val, 1)
            return None

        # 5. Totalizzatori cumulativi energia (Wh -> kWh)
        if self.entity_description.key in ("E0_runtime", "ETotal", "E0_7D", "E0_30D", "E0_1Y"):
            raw_val = self.coordinator.data.get(self.entity_description.key)
            if raw_val is None and self.entity_description.key == "E0_1Y":
                raw_val = self.coordinator.data.get("EYear")
            return round(float(raw_val) / 1000.0, 2) if raw_val is not None else None

        # 6. Stato Operativo Inverter (GlobalState)
        if self.entity_description.key == "GlobalState":
            raw_state = (
                self.coordinator.data.get("GlobalState")
                or self.coordinator.data.get("InverterState")
            )
            if raw_state is None:
                return "Sconosciuto"
            try:
                code = int(float(raw_state))
                return GLOBAL_STATE_MAP.get(code, f"Stato {code}")
            except (ValueError, TypeError):
                return str(raw_state)

        # 7. Stato Allarme Inverter (Dinamico e fedele al firmware dell'inverter)
        if self.entity_description.key == "AlarmState":
            raw_alarm = (
                self.coordinator.data.get("AlarmState")
                or self.coordinator.data.get("AlarmCode")
                or self.coordinator.data.get("Alarm")
                or self.coordinator.data.get("AlarmDesc")
            )
            if not raw_alarm or str(raw_alarm).strip() in (
                "0",
                "0.0",
                "None",
                "No Alarm",
                "OK",
                "null",
            ):
                return "Nessun Allarme"

            return str(raw_alarm).strip()

        # 8. Temperature e altri valori diretti
        raw_val = self.coordinator.data.get(self.entity_description.key)
        if raw_val is None:
            return None

        return round(float(raw_val), 1 if "Temp" in self.entity_description.key else 2)
