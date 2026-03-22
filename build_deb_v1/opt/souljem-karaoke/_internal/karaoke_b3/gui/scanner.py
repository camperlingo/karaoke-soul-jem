import os
import tkinter as tk
import uuid

class LocalScanner:
    def __init__(self, listbox, status_label):
        """
        Inizializza lo scanner per i file locali.
        Gestisce la visualizzazione ad albero dei file e delle cartelle.
        :param listbox: Il widget tk.Listbox da popolare.
        :param status_label: La label per i messaggi di stato.
        """
        self.lsb = listbox
        self.lbl_status = status_label
        
        # --- FIX: Rinominato da current_path a current_folder per compatibilità con MainWindow ---
        self.current_folder = "" 
        
        self.all_files = [] # Cache interna per permettere il filtraggio istantaneo
        
        # ==========================================================
        # CONFIGURAZIONE ESTENSIONI
        # ==========================================================
        # Supporto esteso per Video, Audio e formati Karaoke specifici
        self.extensions = (
            '.mp4', '.avi', '.mkv', '.webm', '.flv',  # Formati Video
            '.mp3', '.wav', '.m4a', '.wma', '.aac',  # Formati Audio
            '.zip', '.cdg'                           # Formati Karaoke CDG
        )

    # ==========================================================
    # LOGICA DI SCANSIONE DISCO
    # ==========================================================
    def scan(self, path):
        """
        Scansiona la cartella specificata e aggiorna l'interfaccia.
        Include filtri per file nascosti e gestione permessi.
        """
        if not path or not os.path.exists(path):
            print(f"[SCANNER] Attenzione: Percorso non trovato o non valido: {path}")
            return
            
        try:
            # Normalizzazione percorso per evitare bug su Linux/Windows
            # --- FIX: Uso current_folder ---
            self.current_folder = os.path.abspath(path)
            self.all_files = []
            
            # --- Gestione Navigazione Superiore ---
            # Aggiunge l'opzione per tornare alla cartella precedente
            parent = os.path.dirname(self.current_folder)
            if parent != self.current_folder:
                self.all_files.append("⬅️ TORNA INDIETRO")

            # --- Lettura Directory ---
            # Separazione cartelle e file per una visualizzazione ordinata
            items = sorted(os.listdir(self.current_folder))
            
            dirs = []
            files = []
            
            for item in items:
                # Ignora file di sistema o nascosti (es. .DS_Store o .trash)
                if item.startswith('.'): 
                    continue
                    
                full_p = os.path.join(self.current_folder, item)
                
                try:
                    if os.path.isdir(full_p):
                        dirs.append(f"📁 {item}")
                    elif item.lower().endswith(self.extensions):
                        files.append(item)
                except (PermissionError, OSError):
                    # Salta silenziosamente elementi inaccessibili
                    continue
            
            # Unione: Prima le cartelle, poi i file musicali
            self.all_files.extend(dirs)
            self.all_files.extend(files)

            # Aggiornamento fisico della lista
            self.update_list()
            
            # Aggiornamento etichetta di stato nel footer
            if self.lbl_status:
                count = len(files)
                folder_name = os.path.basename(self.current_folder) or self.current_folder
                self.lbl_status.config(
                    text=f"ARCHIVIO: {folder_name} ({count} basi trovate)", 
                    fg="cyan"
                )
                
        except PermissionError:
            print("[SCANNER] Errore: Permessi insufficienti per la cartella.")
            if self.lbl_status: 
                self.lbl_status.config(text="ERRORE: ACCESSO NEGATO", fg="red")
        except Exception as e:
            print(f"[SCANNER] Errore critico: {e}")
            if self.lbl_status: 
                self.lbl_status.config(text=f"ERRORE SCAN: {str(e)[:20]}", fg="red")

    # ==========================================================
    # RISOLUZIONE PERCORSI
    # ==========================================================
    def get_path_from_item(self, item_string):
        """
        Converte la stringa selezionata nella Listbox in un path assoluto.
        Fondamentale per il passaggio dati alle WindowActions.
        """
        if not item_string:
            return None
            
        # Caso navigazione
        if "⬅️" in item_string:
            return os.path.dirname(self.current_folder)
            
        # Caso cartella (pulizia emoji)
        if "📁" in item_string:
            folder_name = item_string.replace("📁 ", "").strip()
            return os.path.join(self.current_folder, folder_name)
            
        # Caso file standard
        return os.path.join(self.current_folder, item_string)

    # ==========================================================
    # GESTIONE INTERFACCIA (LISTBOX)
    # ==========================================================
    def update_list(self, filter_text=""):
        """
        Filtra e visualizza gli elementi nella Listbox.
        Ottimizzato per ricerche rapide in tempo reale.
        """
        try:
            if not self.lsb.winfo_exists(): 
                return
        except:
            return
            
        self.lsb.delete(0, tk.END)
        f_text = filter_text.lower().strip()
        
        for item in self.all_files:
            # Logica di filtraggio: mostra se corrisponde o se è un comando di sistema
            if not f_text or f_text in item.lower() or "⬅️" in item:
                self.lsb.insert(tk.END, item)
        
        # Riapplica lo stile visivo scuro
        self.lsb.configure(bg='#111', fg='white', selectbackground="#005a9e")

    def generate_unique_id(self):
        """
        Genera un identificativo per tracciare il file nel processo di encoding.
        """
        return uuid.uuid4().hex[:10]

    def clear(self):
        """Reset completo della cache e della vista."""
        self.all_files = []
        try:
            self.lsb.delete(0, tk.END)
        except:
            pass
