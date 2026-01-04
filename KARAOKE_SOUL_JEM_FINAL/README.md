# 🎤 Karaoke Soul Jem

**Karaoke Soul Jem** è un sistema professionale di Karaoke e Radio "lightweight", nato dalla necessità di avere un software fluido e affidabile anche su hardware datato (testato con successo su Acer Aspire con processore AMD E1-7010 e 2GB di RAM).

## 🌟 Filosofia del Progetto
A differenza di molti software moderni, **Soul Jem** non cerca la complessità, ma la stabilità. L'applicazione gestisce in modo intelligente i processi di sistema per garantire che la musica non si fermi mai, offrendo un'interfaccia reattiva e un controllo totale all'operatore.

## ⚠️ Nota per gli Sviluppatori (Ambiente Virtuale)
Per il corretto funzionamento dei moduli di download (`download_mp3.py` e `scarica_mp3.py`), è **obbligatorio** utilizzare un ambiente virtuale (venv). Questo evita conflitti con le politiche di gestione dei pacchetti del sistema operativo.

### Configurazione rapida:
1. **Crea l'ambiente**: `python3 -m venv venv`
2. **Attiva l'ambiente**: `source venv/bin/activate`
3. **Installa le dipendenze**: `pip install -r requirements.txt`

## 🛠️ Storia dello Sviluppo: Il caso OBS
Durante la fase di prototipazione, abbiamo integrato il supporto per **OBS (Open Broadcaster Software)** tramite WebSocket per gestire il mirroring video. 

Nonostante il successo tecnico del controller, abbiamo deciso di **abbandonare questa strada** per i seguenti motivi:
* **Carico CPU**: OBS risultava eccessivamente pesante per i processori di fascia bassa.
* **Latenza**: Il mirroring tramite OBS causava micro-scatti che compromettevano l'esperienza del cantante.

**Soluzione attuale**: Abbiamo optato per una gestione diretta di **mpv** e **chromium**, eliminando ogni intermediario pesante e massimizzando le prestazioni.

## 🚀 Obiettivi Futuri (Roadmap)
Il viaggio di Soul Jem è appena iniziato. I prossimi passi prevedono:
* **Supporto MIDI**: Integrazione di un sintonizzatore MIDI Open Source.
* **Pentagramma Dinamico**: Un popup dedicato per i file MIDI che mostri in tempo reale il pentagramma con note o accordi.
* **Studio degli Strumenti**: Possibilità di selezionare e visualizzare la partitura di singoli strumenti all'interno della traccia MIDI.

## 📦 Installazione Utenti (Linux)
Se desideri semplicemente utilizzare l'applicazione senza modificare il codice, scarica il pacchetto ufficiale `.deb` dalla sezione **Releases** di questo repository. Una volta scaricato, installalo con:
`sudo apt install ./karaoke-soul-jem.deb`

---
*Sviluppato con passione per mantenere viva la musica su ogni computer.*
