import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """
    Gestisce il caricamento e il salvataggio della configurazione
    dell'applicazione da un file JSON.
    """
    
    # Valori di default
    DEFAULT_CONFIG = {
        "volume": 75,
        "window_width": 1024,
        "window_height": 768,
        "window_maximized": False,
        "second_monitor_index": 1,
        "last_played_file": None,
        "pitch_semitones": 0.0,
        "is_turbo": False,
        "radio_bg_image": None,       # NUOVO: Memoria Immagine
        "viz_video_folder": None      # NUOVO: Memoria Cartella Video
    }

    def __init__(self, config_file="karaoke_config.json"):
        self.config_file = os.path.join(os.path.expanduser('~'), f".config/karaoke_b3/{config_file}")
        
        # Assicura che la directory esista
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Applica i default
        self.__dict__.update(self.DEFAULT_CONFIG)
        
        # Sovrascrivi con i valori salvati
        self.load()
        logger.info("Configurazione inizializzata")

    def load(self):
        """Carica la configurazione dal file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                    # Carica solo le chiavi che sono presenti nei DEFAULT per sicurezza
                    for key in self.DEFAULT_CONFIG:
                        if key in data:
                            setattr(self, key, data[key])
                            
                logger.info("Configurazione caricata")
            except Exception as e:
                logger.error(f"Errore durante il caricamento della configurazione: {e}")
                
        # Se il file non esiste o fallisce il caricamento, mantiene i DEFAULT.
        
    def save(self):
        """Salva la configurazione sul file."""
        data = {}
        # Salva solo le chiavi definite nei DEFAULT
        for key in self.DEFAULT_CONFIG:
            data[key] = getattr(self, key)
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info("Configurazione salvata")
        except Exception as e:
            logger.error(f"Errore durante il salvataggio della configurazione: {e}")

    # NUOVO METODO AGGIUNTO per soddisfare MediaPlayer
    def get_player_setting(self, key, default=None):
        """
        Ottiene le impostazioni del player (volume, pitch, ecc.) dagli attributi della classe.
        Questo metodo è richiesto dal modulo player.
        """
        # Controlla prima se l'attributo è stato impostato o caricato
        if hasattr(self, key):
            return getattr(self, key)
            
        # In caso contrario, restituisce il default (della classe o passato come argomento)
        return self.DEFAULT_CONFIG.get(key, default)
        
    # Helper per ottenere i valori (opzionale, ma mantiene la coerenza)
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self.DEFAULT_CONFIG:
             return self.DEFAULT_CONFIG[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
