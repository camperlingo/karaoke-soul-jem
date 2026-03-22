import tkinter as tk
import os
import sys
import subprocess
import platform  # Fondamentale per rilevare il sistema operativo

# ==========================================================
# CONFIGURAZIONE PERCORSI E SISTEMA
# ==========================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'karaoke_b3'))

# Impostazioni specifiche per Linux
if platform.system() != "Windows":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    os.environ['GDK_BACKEND'] = 'x11' 

# ==========================================================
# IMPORTAZIONE MODULI
# ==========================================================
try:
    from karaoke_b3.core.player import KaraokePlayer
    from karaoke_b3.core.bg_manager import BackgroundManager
    from karaoke_b3.core.media_logic import MediaLogic 
    from karaoke_b3.gui.main_window import MainWindow
except ImportError:
    from core.player import KaraokePlayer
    from core.bg_manager import BackgroundManager
    from core.media_logic import MediaLogic
    from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title(f"KARAOKE CLEAN PROFESSIONAL - Running on {platform.system()}")
    root.configure(bg='#111') 

    # Zoom intelligente in base al sistema
    if platform.system() == "Windows":
        root.state('zoomed')
    else:
        root.attributes('-zoomed', True)

    bg_music = BackgroundManager()
    player = KaraokePlayer()
    processor = MediaLogic(None) 
    app_gui = MainWindow(root, player, processor, bg_music)
    
    processor.mw = app_gui
    player.mw = app_gui

    def on_closing():
        print(f"\n[SISTEMA] Chiusura su {platform.system()}...")
        try:
            # Chiusura SMTube cross-platform
            if platform.system() == "Windows":
                # Comando specifico Windows per killare il processo
                subprocess.run(["taskkill", "/F", "/IM", "smtube.exe", "/T"], 
                             capture_output=True, check=False)
            else:
                # Comando Linux
                subprocess.run(["pkill", "-9", "-f", "smtube"], check=False)
            
            if hasattr(app_gui, 'stop_karaoke_video'):
                app_gui.stop_karaoke_video()
            if bg_music: bg_music.stop()
            if player: player.cleanup()
        except:
            pass
        finally:
            root.destroy()
            os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
