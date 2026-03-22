# KARAOKE CLEAN - Sviluppo & Ottimizzazione

## 🟢 FASE 1: Stabilità Locale (Hardware AMD R2 / Linux)
*Obiettivo: Rendere l'app perfetta sul PC di sviluppo attuale.*

- [x] **Gestione Audio:** Risolto conflitto Radio/Player con logica "Ducking" e protezione switch.
- [x] **Chiusura Atomica:** Eliminato il freeze all'uscita (kill dei processi MPV e salvataggio sessione).
- [x] **Ottimizzazione AMD:** MPV configurato su VA-API (video_sync=audio, cache RAM 150MB).
- [x] **Performance UI:** Implementato "Loop Immortale" per impedire il blocco della barra di avanzamento.
- [x] **Fix Radio Muta:** Implementato ripristino forzato (`force=True`) su stop e fine brano.

## 🟡 FASE 2: Consolidamento
*Obiettivo: Pulizia del codice e preparazione alla condivisione.*

- [x] **Pulizia Architettura:** Rimossi moduli obsoleti (`processor`, `engine`, `left_panel`) e centralizzato su `core/` e `gui/`.
- [x] **Salvataggio Sessione:** Il diario (playlist) viene salvato su JSON e ripristinato al riavvio.
- [ ] **Log Cleanup:** Rimuovere i print di debug residui per la versione di produzione.
- [ ] **Error Handling:** Migliorare la gestione di file video corrotti durante il download.

## 🔵 FASE 3: Portabilità & Open Source
*Obiettivo: Rendere l'app universale per la community.*

- [ ] **Interfaccia Grafica:** Valutare restyling moderno (icone vettoriali, temi).
- [ ] **Configurazione Dinamica:** Creare un file `settings.json` per driver video e cartelle predefinite.
- [ ] **Pacchettizzazione:** Creare script di installazione automatica.

---
*Stato: STABILE (v1.0)*
*Ultimo aggiornamento: 30 Dicembre 2025*
