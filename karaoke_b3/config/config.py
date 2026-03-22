import os
import logging
from pathlib import Path

class Config:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.CONFIG_DIR = self.BASE_DIR / "config"
        
        # Crea le directory se non esistono
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.CONFIG_DIR.mkdir(exist_ok=True)
        
        self.LOG_LEVEL = logging.INFO
        self.LOG_FILE = str(self.LOGS_DIR / "karaoke_b3.log")
        
        # Configurazione MPV
        self.MPV_OPTIONS = {
            'hwdec': 'auto',
            'vo': 'x11',
            'input-vo-keyboard': 'no',
            'input-cursor': 'no',
            'cursor-autohide': 'always',
            'force-window': 'yes',
            'keep-open': 'yes',
            'idle': 'yes',
            'msg-level': 'all=info'
        }
        
        # Configurazione GUI
        self.WINDOW_TITLE = "Karaoke B3"
        self.WINDOW_DEFAULT_SIZE = (1024, 768)
