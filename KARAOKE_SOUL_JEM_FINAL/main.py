import tkinter as tk
import os
import sys

# ==========================================================
# CONFIGURAZIONE PERCORSI (FIX PER ERRORE 'core')
# ==========================================================
# Questa riga dice a Python: "Guarda anche dentro la cartella karaoke_b3"
# Risolve l'errore No module named 'core' una volta per tutte.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'karaoke_b3'))

# Impedisce i warning su Linux
os.environ['TK_SILENCE_DEPRECATION'] = '1'
if sys.platform.startswith('linux'):
    os.environ['GDK_BACKEND'] = 'x11' 

# ==========================================================
# IMPORTAZIONE MODULI (Percorsi Assoluti)
# ==========================================================
try:
    from karaoke_b3.core.player import KaraokePlayer
    from karaoke_b3.core.bg_manager import BackgroundManager
    from karaoke_b3.core.media_logic import MediaLogic 
    from karaoke_b3.gui.main_window import MainWindow
except ImportError as e:
    print(f"ERRORE CRITICO DI CARICAMENTO: {e}")
    # Se il primo fallisce, proviamo il secondo percorso
    try:
        from core.player import KaraokePlayer
        from core.bg_manager import BackgroundManager
        from core.media_logic import MediaLogic
        from gui.main_window import MainWindow
    except ImportError as e2:
        print(f"IMPOSSIBILE AVVIARE: Moduli non trovati.\nErrore 1: {e}\nErrore 2: {e2}")
        sys.exit(1)

def main():
    root = tk.Tk()
    root.title("KARAOKE CLEAN PROFESSIONAL")
    root.configure(bg='#111') 

    if sys.platform.startswith('linux'):
        root.attributes('-zoomed', True)
    else:
        root.state('zoomed')

    # Inizializzazione Motori
    bg_music = BackgroundManager()
    player = KaraokePlayer()
    processor = MediaLogic(None) 
    
    # Inizializzazione GUI
    app_gui = MainWindow(root, player, processor, bg_music)
    
    processor.mw = app_gui
    player.mw = app_gui

    root.lift()

    def on_closing():
        print("\n[SISTEMA] Chiusura di sicurezza in corso...")
        try:
            # Chiama la funzione di stop che abbiamo messo in MainWindow per OBS
            if hasattr(app_gui, 'stop_karaoke_video'):
                app_gui.stop_karaoke_video()
            
            if bg_music: bg_music.stop()
            if player: player.cleanup()
            
            print("[SISTEMA] Risorse rilasciate. Arrivederci!")
        except Exception as e:
            print(f"[ERRORE] Durante la chiusura: {e}")
        
        root.quit()
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()

if __name__ == "__main__":
    main()
