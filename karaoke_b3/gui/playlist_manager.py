import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class PlaylistManager:
    def __init__(self, tree, playlist_data, refresh_callback):
        self.tree = tree
        self.playlist_data = playlist_data
        self.refresh_callback = refresh_callback

    def save_item_to_disk(self, scanner_ref):
        """Sposta il file scaricato in una cartella scelta dall'utente"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un brano dalla playlist per salvarlo.")
            return
        
        idx = self.tree.index(sel[0])
        data = self.playlist_data[idx]
        
        # Verifica se è un file temporaneo (nella cartella cache)
        if not data['path'] or "cache" not in data['path']:
            messagebox.showinfo("Info", "Questo brano è già nell'archivio locale.")
            return

        dest_dir = filedialog.askdirectory(title="In quale cartella vuoi salvare il brano?")
        if dest_dir:
            # Pulizia nome file
            clean_name = f"{data['song']}.mp4".replace("/", "-").replace("\\", "-")
            dest_path = os.path.join(dest_dir, clean_name)
            
            try:
                shutil.move(data['path'], dest_path)
                data['path'] = dest_path # Aggiorna il percorso in memoria
                messagebox.showinfo("Successo", f"Brano salvato correttamente: {clean_name}")
                
                # Se la cartella di destinazione è quella attualmente aperta a sinistra, rinfresca
                if scanner_ref.current_path == dest_dir:
                    scanner_ref.scan(dest_dir)
                    
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Errore di salvataggio", str(e))
