# FIMER / ABB UNO-DM REST Integration per Home Assistant

Integrazione personalizzata per **Home Assistant** per monitorare localmente gli inverter **FIMER / ABB UNO-DM-4.6-TL-PLUS** tramite le API REST native della scheda Wi-Fi integrata.

Questa integrazione comunica direttamente in rete locale (LAN) con l'inverter, senza dipendere dal cloud.

---

## Caratteristiche Principali

- **100% Locale e Veloce:** Interroga l'endpoint nativo `/v1/livedata` con autenticazione HTTP Basic.
- **Supporto Multi-MPPT:** Monitoraggio separato di tensione, corrente e calcolo istantaneo della potenza (W) per Stringa 1 e Stringa 2.
- **Diagnostica Completa:**
  - Controllo di isolamento ($R_{\text{iso}}$ in $\text{M}\Omega$).
  - Monitoraggio correnti di dispersione a terra ($I_{\text{leak}}$ in $\text{mA}$).
  - Monitoraggio delle 3 temperature fisiche: Stadio AC (`TempInv`), Stadio Booster DC (`TempBst`) e Sistema interno (`Temp1`).
  - Monitoraggio e stato della ventola di raffreddamento (RPM e stato di marcia).
  - Ciclo di stato operativo globale dell'inverter (In Produzione, Sleep, Sincronizzazione, ecc.).
  - **Allarmi dinamici nativi:** Decodifica in tempo reale dei warning ed errori proprietari dell'inverter (es. `W002 - Input UV`, `W010 - Fan fault`, `W032L - Early Power-off`).
- **Metriche Energetiche Complete:** Statistiche cumulative (Oggi, 7 giorni, 30 giorni, Anno Corrente e Totale Lifetime).
- **Compatibilità Energy Dashboard:** Sensori configurati nativamente con classi `total_increasing` e `device_class: energy`.
- **Calcolo Efficienza Real-time:** Rapporto istantaneo tra potenza DC generata e potenza AC immessa in rete.

---

## Tabella Sensori e Mappatura JSON

| Sensore | Chiave JSON Inverter | Unità | Descrizione |
| :--- | :---: | :---: | :--- |
| **Potenza AC Attuale** | `Pgrid` / `PacTogrid` | W | Potenza istantanea immessa in rete |
| **Potenza DC Totale** | `Pin` | W | Potenza DC complessiva dai moduli fotovoltaici |
| **Potenza Stringa 1** | `Pin1` *(o $V_1 \times I_1$)* | W | Potenza canale MPPT 1 |
| **Potenza Stringa 2** | `Pin2` *(o $V_2 \times I_2$)* | W | Potenza canale MPPT 2 |
| **Picco Potenza Oggi** | `Ppeak` | W | Massimo picco di potenza generato nella giornata |
| **Efficienza Conversione** | *Calcolato* | % | Rendimento istantaneo di conversione ($P_{\text{grid}} / P_{\text{in}}$) |
| **Produzione Oggi** | `E0_runtime` | kWh | Energia prodotta nella giornata corrente |
| **Produzione Ultimi 7 Giorni** | `E0_7D` | kWh | Energia prodotta negli ultimi 7 giorni |
| **Produzione Ultimi 30 Giorni** | `E0_30D` | kWh | Energia prodotta negli ultimi 30 giorni |
| **Produzione Anno Corrente** | `E0_1Y` *(o `EYear`)* | kWh | Contatore progressivo dell'anno solare in corso |
| **Produzione Totale (Lifetime)** | `ETotal` | kWh | Contatore progressivo storico totale di vita dell'inverter |
| **Tensione Stringa 1** | `Vin1` | V | Tensione continua MPPT 1 |
| **Corrente Stringa 1** | `Iin1` | A | Corrente continua MPPT 1 |
| **Tensione Stringa 2** | `Vin2` | V | Tensione continua MPPT 2 |
| **Corrente Stringa 2** | `Iin2` | A | Corrente continua MPPT 2 |
| **Tensione di Rete** | `Vgrid` | V | Tensione alternata della rete elettrica (AC) |
| **Frequenza di Rete** | `Fgrid` | Hz | Frequenza di rete (50 Hz) |
| **Temperatura Inverter** | `TempInv` | °C | Temperatura stadio finale ponte AC |
| **Temperatura Stadio Booster** | `TempBst` | °C | Temperatura stadio elevatore DC-DC |
| **Temperatura Sistema** | `Temp1` | °C | Temperatura interna della scheda di controllo |
| **Resistenza di Isolamento** | `Riso` | MΩ | Resistenza di isolamento verso terra |
| **Corrente Dispersione a Terra**| `Ileak` / `IleakDC` | mA | Corrente differenziale di fuga a terra |
| **Velocità Ventola** | `Fan1rpm` | RPM | Velocità di rotazione della ventola interna |
| **Stato Operativo Inverter** | `GlobState` | Testo | Stato ciclo operativo (es. *In Produzione (Run)*, *Standby Notturno (Sleep)*) |
| **Stato Allarme Inverter** | `AlarmState` | Testo | Diagnostica allarmi nativa (es. `W002 - Input UV`, `W010 - Fan fault`, `Nessun Allarme`) |

---

## Installazione

### Metodo 1: Tramite HACS (Consigliato)

1. Apri **HACS** nel tuo Home Assistant.
2. Clicca sui tre puntini in alto a destra e seleziona **Repository personalizzati**.
3. Incolla l'URL del repository: `https://github.com/nanni85/ha-fimer-rest`.
4. Seleziona la categoria **Integrazione** e clicca su **Aggiungi**.
5. Cerca **FIMER / ABB UNO-DM Local**, clicca su **Scarica** e seleziona l'ultima versione.
6. Riavvia Home Assistant.

### Metodo 2: Installazione Manuale

1. Scarica lo zip dell'ultima release da GitHub.
2. Estrai la cartella `custom_components/fimer_rest/`.
3. Copia l'intera cartella `fimer_rest` all'interno della directory `config/custom_components/` della tua installazione di Home Assistant.
4. Riavvia Home Assistant.

---

## Configurazione

1. In Home Assistant vai su **Impostazioni** > **Dispositivi e servizi**.
2. Clicca su **Aggiungi integrazione** in basso a destra.
3. Cerca **FIMER / ABB UNO-DM Local**.
4. Inserisci i parametri richiesti:
   - **Host / IP**: L'indirizzo IP statico assegnato all'inverter (es. `192.168.0.193`).
   - **Username**: Il nome utente della web UI dell'inverter.
   - **Password**: La password di accesso all'inverter.
5. Clicca su **Invia**. Il dispositivo e tutte le relative entità verranno generate automaticamente.

---

## Configurazione Energy Dashboard

Per monitorare la produzione nell'**Energy Dashboard** nativa di Home Assistant:

1. Vai su **Impostazioni** > **Dashboard** > **Energia**.
2. Nella sezione **Pannelli solari**, clicca su **Aggiungi produzione solare**.
3. Seleziona come sensore di energia:
   - `sensor.fimer_uno_dm_4_6_tl_plus_produzione_totale_lifetime` (oppure `sensor.inverter_etotal` se hai mantenuto il vecchio ID entità).
4. Salva le modifiche.

---

## Esempio Automazione Notifiche (Allarmi Reali)

Ricevi una notifica push sullo smartphone escludendo i warning transitori del tramonto (`W001`, `W002`, `W032L`):

```yaml
alias: "FIMER: Notifica Anomalie Inverter"
trigger:
  - platform: state
    entity_id: sensor.fimer_uno_dm_4_6_tl_plus_stato_allarme_inverter
condition:
  - condition: template
    value_template: >
      {% set s = trigger.to_state.state %}
      {{ s not in ['Nessun Allarme', 'unknown', 'unavailable']
         and not ('W001' in s or 'W002' in s or 'W032' in s) }}
action:
  - action: notify.notify
    data:
      title: "⚠️ Anomalia FIMER Inverter"
      message: "L'inverter segnala: {{ trigger.to_state.state }}"
