import pyautogui
import time
# IMPORT CORRETTO: Dobbiamo dire a Python di passare da karaoke_b3
from karaoke_b3.core.logger import info, warning

class OBSController:
    """Gestisce OBS tramite Hotkey per l'hardware AMD R2."""
    def __init__(self):
        self.HOTKEY_SHOW_VIDEO = 'f10' 
        self.HOTKEY_HIDE_VIDEO = 'f11' 

    def set_stato_karaoke(self):
        info("[OBS] Attivazione STATO 2: KARAOKE ON")
        pyautogui.press(self.HOTKEY_SHOW_VIDEO)

    def set_stato_idle(self):
        info("[OBS] Attivazione STATO 3: IDLE")
        pyautogui.press(self.HOTKEY_HIDE_VIDEO)
