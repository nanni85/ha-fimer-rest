# FIMER / ABB UNO-DM REST Integration per Home Assistant

Integrazione personalizzata per **Home Assistant** per monitorare localmente gli inverter **FIMER / UNO-DM-4.6-TL-PLUS ** tramite le API REST native della scheda Wi-Fi integrata.

Questa integrazione comunica direttamente in rete locale (LAN) con l'inverter, senza dipendere dal cloud Aurora Vision né da bridge esterni.

---

## Caratteristiche Principali

- **100% Locale e Veloce:** Interroga l'endpoint nativo `/v1/livedata` con autenticazione HTTP Basic.
- **Supporto Multi-MPPT:** Monitoraggio separato di tensione, corrente e calcolo istantaneo della potenza (W) per Stringa 1 e Stringa 2.
- **Diagnostica Completa:**
  - Controllo di isolamento ($R_{\text{iso}}$ in $\text{M}\Omega$).
  - Monitoraggio correnti di dispersione a terra ($I_{\text{leak}}$ in $\text{mA}$).
  - Monitoraggio delle 3 temperature fisiche: Stadio AC (`TempInv`), Stadio Booster DC (`TempBst`) e Sistema interno (`Temp1`).
  - Monitoraggio e stato della ventola di raffreddamento (RPM e stato di marcia).
- **Metriche Energetiche:** Statistiche cumulative (Oggi, 7 giorni, 30 giorni e Totale di vita impianto).
- **Compatibilità Energy Dashboard:** Sensori configurati nativamente con classi `total_increasing` e `device_class: energy`.
- **Calcolo Efficienza Real-time:** Rapporto istantaneo tra potenza DC generata e potenza AC immessa in rete.

---

## Sensori Disponibili

| Sensore | Unità | Descrizione |
| :--- | :---: | :--- |
| **Potenza AC Attuale** | W | Potenza immessa istantaneamente in rete |
| **Potenza DC Totale** | W | Potenza totale generata dai pannelli solari |
| **Potenza Stringa 1** | W | Potenza calcolata MPPT 1 ($V_1 \times I_1$) |
| **Potenza Stringa 2** | W | Potenza calcolata MPPT 2 ($V_2 \times I_2$) |
| **Picco Potenza Oggi** | W | Valore massimo di potenza raggiunto nella giornata |
| **Efficienza Conversione** | % | Rendimento istantaneo dell'inverter |
| **Produzione Oggi** | kWh | Energia prodotta nella giornata corrente |
| **Produzione Totale** | kWh | Contatore cumulativo totale dell'inverter |
| **Produzione Ultimi 7 Giorni** | kWh | Energia prodotta nell'ultima settimana |
| **Produzione Ultimi 30 Giorni** | kWh | Energia prodotta nell'ultimo mese |
| **Tensione / Corrente Stringa 1** | V / A | Tensione e corrente sul canale MPPT 1 |
| **Tensione / Corrente Stringa 2** | V / A | Tensione e corrente sul canale MPPT 2 |
| **Tensione di Rete** | V | Tensione alternata della rete elettrica (AC) |
| **Frequenza di Rete** | Hz | Frequenza di rete (50 Hz) |
| **Temperatura Inverter** | °C | Temperatura del ponte inverter AC |
| **Temperatura Stadio Booster** | °C | Temperatura dello stadio elevatore DC-DC |
| **Temperatura Sistema** | °C | Temperatura interna della scheda di controllo |
| **Resistenza di Isolamento** | MΩ | Resistenza di isolamento verso terra |
| **Corrente Dispersione a Terra**| mA | Corrente differenziale di fuga |
| **Velocità Ventola** | RPM | Giri al minuto della ventola di raffreddamento |
| **Stato Ventola** | On/Off | Stato operativo della ventola (in marcia o ferma) |
| **Stato Operativo Inverter** | Testo | Ciclo operativo (In Produzione, Sleep Notturno, Sincronizzazione, ecc.) |
| **Stato Allarme Inverter** | Testo | Notifica dinamica allarmi/warning proprietari FIMER (es. `W002 - Input UV`, `W010 - Fan fault`, `Nessun Allarme`) |
| **Stato Connessione** | Testo | Stato raggiungibilità LAN dell'inverter |
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
   - **Username**: Il nome utente della web UI dell'inverter (es. `admin` o il tuo utente configurato).
   - **Password**: La password di accesso all'inverter.
5. Clicca su **Invia**. Il dispositivo e tutte le relative entità verranno generate automaticamente.

---

## Configurazione Energy Dashboard

Per monitorare la produzione nell'**Energy Dashboard** nativa di Home Assistant:

1. Vai su **Impostazioni** > **Dashboard** > **Energia**.
2. Nella sezione **Pannelli solari**, clicca su **Aggiungi produzione solare**.
3. Seleziona l'entità:
   - `sensor.fimer_uno_dm_4_6_tl_plus_produzione_totale` (oppure `sensor.inverter_etotal` se hai mantenuto il vecchio ID).
4. Salva le modifiche.

---

## Licenza

Questo progetto è rilasciato sotto licenza MIT.
