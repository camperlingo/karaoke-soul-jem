import logging
import mpv
import os
from gi.repository import Gdk

logger = logging.getLogger(__name__)

class SecondMonitor:
    """
    Gestisce la finestra del secondo monitor (schermo pubblico) usando un'istanza 
    nativa e separata di MPV per la visualizzazione fullscreen.
    """
    def __init__(self, player_creator_func, config):
        # player_creator_func è la funzione di callback per creare il player (in main_window)
        self.player_creator_func = player_creator_func
        self.config = config
        self.player = None  # Il player verrà creato solo al primo self.show()
        self.is_visible = False
        
        # 1. Trova il monitor su cui mostrare la finestra
        self.display = Gdk.Display.get_default()
        self.n_monitors = self.display.get_n_monitors()
        
        # Tentativo di usare il monitor specificato in config, altrimenti il secondo disponibile
        monitor_index = self.config.second_monitor_index
        if monitor_index < 0 or monitor_index >= self.n_monitors:
            # Se l'indice è non valido, usiamo il primo monitor disponibile dopo il principale (se esiste)
            monitor_index = 1 if self.n_monitors > 1 else -1

        self.target_monitor_index = monitor_index

        logger.info(f"Secondo monitor inizializzato (Monitor disponibili: {self.n_monitors}, Target: {self.target_monitor_index})")

    def _create_player_if_needed(self):
        """Crea l'istanza MPV nativa se non esiste."""
        if self.player is None:
            self.player = self.player_creator_func()
            if self.player:
                logger.info("Player nativo MPV per secondo monitor creato con successo.")
            else:
                logger.error("Impossibile creare il player nativo MPV per il secondo monitor.")
                return False
        return True

    def _set_fullscreen_on_monitor(self):
        """Applica fullscreen sul monitor di destinazione usando le proprietà MPV."""
        if not self.player:
            return

        try:
            # Opzione 1: usa mpv-monitor-index per posizionare e fullscreen
            if self.target_monitor_index >= 0:
                self.player.set_property('mpv-monitor-index', self.target_monitor_index)
                self.player.set_property('fullscreen', True)
                logger.debug(f"Impostato fullscreen sul monitor: {self.target_monitor_index}")
            else:
                # Se c'è solo un monitor o l'indice non è valido, usa il fullscreen normale
                self.player.set_property('fullscreen', True)
                logger.debug("Impostato fullscreen normale (monitor unico).")

        except Exception as e:
            logger.error(f"Errore nell'impostare il fullscreen/monitor: {str(e)}")
            # Rimuoviamo il tentativo di resize che può interferire
            
    def show(self, file_path=None):
        """
        Mostra la finestra del player nativo MPV sul monitor di destinazione.
        """
        if not self._create_player_if_needed():
            return

        if self.is_visible:
            # Se è già visibile, non facciamo nulla a meno che non si cambi file
            if file_path and self.player.path != file_path:
                 try:
                    self.player.loadfile(file_path)
                    logger.info(f"File ricaricato su secondo monitor: {file_path}")
                 except Exception as e:
                    logger.error(f"Errore nel ricaricamento del file su secondo monitor: {str(e)}")
            return
            
        try:
            # 1. Se non c'è un file da caricare, carichiamo un file vuoto/idle
            if file_path is None:
                 # Carichiamo uno stato IDLE forzando l'apertura della finestra
                 self.player.set_property('idle', 'yes')
                 self.player.set_property('keep-open', 'yes')
                 self.player.play('')
                 
            # 2. Forziamo l'apertura della finestra e la posizioniamo
            self._set_fullscreen_on_monitor()
            
            self.is_visible = True
            logger.info("Finestra del secondo monitor mostrata.")

        except Exception as e:
            logger.error(f"Errore durante la visualizzazione del secondo monitor: {str(e)}")

    def hide(self):
        """Nasconde e termina la finestra del player nativo MPV."""
        if self.player:
            try:
                # Disattiviamo il fullscreen e chiudiamo la finestra
                self.player.set_property('fullscreen', False)
                self.player.command('quit')
                # Forziamo la distruzione dell'oggetto player in modo che venga ricreato al prossimo show()
                self.player = None 
                self.is_visible = False
                logger.info("Finestra del secondo monitor nascosta.")
            except Exception as e:
                logger.error(f"Errore nel nascondere il secondo monitor: {str(e)}")

    def cleanup(self):
        """Termina il player nativo MPV se esiste."""
        if self.player:
            try:
                self.player.terminate()
                self.player = None
                logger.info("Player nativo MPV terminato.")
            except Exception as e:
                logger.error(f"Errore durante la pulizia del player nativo MPV: {str(e)}")
