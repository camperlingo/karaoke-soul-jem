import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog

class WindowActions:
    def __init__(self, mw):
        """
        Inizializza il controller delle azioni.
        Collega l'interfaccia (mw) alle logiche di business.
        """
        self.mw = mw

        # Inizializzazione sicura della cronologia
        if not hasattr(self.mw, "play_history"):
            self.mw.play_history = []

    # ==========================================================
    # GESTIONE ARCHIVIO (LISTBOX SINISTRA)
    # ==========================================================
    def handle_archive_double_click(self, event):
        """Gestisce il caricamento file o la navigazione cartelle tramite doppio click"""
        sel = self.mw.lsb_files.curselection()
        if not sel:
            return

        item_text = self.mw.lsb_files.get(sel[0])
        # Risoluzione del percorso tramite lo scanner
        path = self.mw.scanner.get_path_from_item(item_text)

        if not path:
            return

        # Rende il percorso assoluto per evitare errori di puntamento
        full_path = os.path.abspath(path)
        print(f"[DEBUG ACTIONS] Archivio -> Selezione: {item_text} | Path: {full_path}")

        # Se è una cartella o il comando 'indietro', naviga
        if os.path.isdir(full_path) or "⬅️" in item_text:
            self.mw.scanner.scan(full_path)
            return

        # Altrimenti è un file: estrae il nome e apre il popup di inserimento
        song_name = os.path.splitext(os.path.basename(full_path))[0]
        self.open_singer_popup(
            initial_name="",
            initial_song=song_name,
            initial_source=full_path,
            initial_pitch=0
        )

    # ==========================================================
    # GESTIONE PLAYLIST (TREEVIEW DESTRA)
    # ==========================================================
    def handle_playlist_double_click(self, event):
        """Apre la modifica per un cantante già in lista"""
        sel = self.mw.tree.selection()
        if not sel:
            return

        try:
            index = self.mw.tree.index(sel[0])
            if index >= len(self.mw.playlist_data):
                return

            item = self.mw.playlist_data[index]
            self.open_singer_popup(
                initial_name=item.get("name", ""),
                initial_song=item.get("song", ""),
                initial_source=item.get("source", ""),
                initial_pitch=item.get("pitch", 0),
                edit_index=index
            )
        except Exception as e:
            print(f"[DEBUG ACTIONS] Errore apertura modifica: {e}")

    def handle_load_button(self):
        """Azione pulsante '+' per inserimento manuale o URL"""
        self.open_singer_popup()
    # ==========================================================
    # CORE: POPUP E CONFERMA DATI (CON PROTEZIONE AMD VAAPI)
    # ==========================================================
    def open_singer_popup(self, initial_name="", initial_song="", initial_source="", initial_pitch=0, edit_index=None):
        """Lancia SingerPopup e gestisce la callback di conferma"""
        from .singer_popup import SingerPopup

        def on_confirmed(name, song, source, pitch, mode):
            try:
                pitch = int(pitch)
            except:
                pitch = 0

            # --- AGGIORNAMENTO RIGA ESISTENTE ---
            if edit_index is not None:
                item = self.mw.playlist_data[edit_index]
                needs_reprocess = (item.get("source") != source or item.get("pitch") != pitch)
                item.update({"name": name, "song": song, "source": source, "pitch": pitch})

                if needs_reprocess:
                    item.update({"path": None, "phase": "WAITING", "progress": 0})
                    # Reset processi pendenti
                    item.pop("_proc", None)
                    item.pop("_stop", None)
                    self.mw.media_logic.start_direct_process(source, pitch, index=edit_index)
                
                self.mw.refresh_tree()
                return

            # --- NUOVO INSERIMENTO ---
            if mode == "karaoke":
                self.mw.pl_logic.add_to_playlist(name, song, source, pitch)
            else:
                # PLAY ISTANTANEO (Salto coda) con Scudo Anti-Bug AMD
                print(f"[SISTEMA] Play istantaneo: Attivazione scudo audio.")
                self.mw._is_switching = True
                self.mw.media_logic.play_now_sync(source, auto_play=True)
                self.mw.root.after(1500, self._reset_switching_flag)

        SingerPopup(self.mw.root, on_confirmed, initial_name, initial_song, initial_source, initial_pitch)

    def _reset_switching_flag(self):
        """Sblocca la gestione dei segnali di stop"""
        self.mw._is_switching = False
        print("[SISTEMA] Scudo audio rimosso. Monitoraggio attivo.")

    # ==========================================================
    # MOTORE DI RIPRODUZIONE (SAFE PLAY)
    # ==========================================================
    def safe_play(self):
        """Esegue il brano selezionato con protezione Ducking"""
        sel = self.mw.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Seleziona un brano dalla playlist.")
            return

        idx = self.mw.tree.index(sel[0])
        item = self.mw.playlist_data[idx]
        
        source = item.get("source", "")
        is_web = source.startswith("http")
        is_mkv = source.lower().endswith(".mkv")
        needs_converted = int(item.get("pitch", 0)) != 0 or is_web or is_mkv
        
        if needs_converted:
            if item.get("phase") != "DONE" or not item.get("path") or not os.path.exists(str(item.get("path"))):
                status_msg = item.get("phase", "NON DEFINITO")
                messagebox.showwarning("Elaborazione", f"Il file ottimizzato AMD non è ancora pronto (Stato: {status_msg})")
                return

        final_path = item.get("path") if item.get("path") else source
        
        self.mw._is_switching = True
        self.safe_play_file(final_path, item.get("song", ""))
        
        # Archiviazione includendo il percorso del file elaborato per il salvataggio futuro
        self._archive_item(item)
        
        self.mw.playlist_data.pop(idx)
        self.mw.refresh_tree()
        self.mw.root.after(1500, self._reset_switching_flag)

    def safe_play_file(self, path, title):
        """Invia comando al motore MediaLogic"""
        self.mw.media_logic.play_now_sync(path, auto_play=True)
        if self.mw.lbl_status:
            self.mw.lbl_status.config(text=f"ON AIR: {title}", fg="#00FF00")
    # ==========================================================
    # ORDINE E SPOSTAMENTO (RIORDINAMENTO MANUALE)
    # ==========================================================
    def move_up(self):
        """Sposta il cantante selezionato verso l'alto"""
        sel = self.mw.tree.selection()
        if not sel: return
        idx = self.mw.tree.index(sel[0])
        if idx > 0:
            self.mw.playlist_data[idx], self.mw.playlist_data[idx-1] = \
                self.mw.playlist_data[idx-1], self.mw.playlist_data[idx]
            self.mw.refresh_tree()
            new_sel = self.mw.tree.get_children()[idx-1]
            self.mw.tree.selection_set(new_sel)

    def move_down(self):
        """Sposta il cantante selezionato verso il basso"""
        sel = self.mw.tree.selection()
        if not sel: return
        idx = self.mw.tree.index(sel[0])
        if idx < len(self.mw.playlist_data) - 1:
            self.mw.playlist_data[idx], self.mw.playlist_data[idx+1] = \
                self.mw.playlist_data[idx+1], self.mw.playlist_data[idx]
            self.mw.refresh_tree()
            new_sel = self.mw.tree.get_children()[idx+1]
            self.mw.tree.selection_set(new_sel)

    # ==========================================================
    # MENU CONTESTUALE E DIARIO (CON SALVATAGGIO BASE)
    # ==========================================================
    def show_context_menu(self, event):
        """Crea e mostra il menu contestuale sulla playlist"""
        iid = self.mw.tree.identify_row(event.y)
        if iid:
            self.mw.tree.selection_set(iid)
            menu = tk.Menu(self.mw.root, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#0078d7")
            menu.add_command(label="▶ Riproduci Subito", command=self.safe_play)
            menu.add_command(label="📝 Modifica Dati", command=lambda: self.handle_playlist_double_click(None))
            menu.add_separator()
            menu.add_command(label="⬆ Sposta Su", command=self.move_up)
            menu.add_command(label="⬇ Sposta Giù", command=self.move_down)
            menu.add_separator()
            menu.add_command(label="🗑 Rimuovi", command=self.remove_singer)
            menu.post(event.x_root, event.y_root)

    def toggle_processing(self):
        """Interrompe o riprende l'encoding/download di una riga"""
        sel = self.mw.tree.selection()
        if not sel: return
        idx = self.mw.tree.index(sel[0])
        item = self.mw.playlist_data[idx]
        phase = item.get("phase")

        if phase in ("DOWNLOAD", "ENCODING"):
            self.mw.media_logic.stop_processing(item)
        elif phase == "PAUSED":
            item.pop("_stop", None)
            self.mw.media_logic.start_direct_process(item.get("source"), item.get("pitch", 0), index=idx)
        self.mw.refresh_tree()

    def _archive_item(self, item):
        """Aggiunge il brano allo storico includendo il file processato"""
        self.mw.play_history.append({
            "name": item.get("name"),
            "song": item.get("song"),
            "source": item.get("source"),
            "pitch": item.get("pitch", 0),
            "processed_path": item.get("path") # Path del file mp4 creato
        })

    def open_history(self):
        """Finestra del Diario con funzione di salvataggio tasto destro"""
        win = tk.Toplevel(self.mw.root)
        win.title("Diario della Serata - [Tasto Destro per Salvare Base]")
        win.geometry("800x500")
        win.configure(bg="#121212")
        
        frame = tk.Frame(win, bg="#121212")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("name", "song", "pitch")
        tree = tk.ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("name", text="Cantante")
        tree.heading("song", text="Canzone")
        tree.heading("pitch", text="Tonalità")
        
        for i, item in enumerate(self.mw.play_history):
            iid = tree.insert("", tk.END, values=(item['name'], item['song'], f"{item['pitch']:+}"))
            tree.item(iid, tags=(str(i),))
            
        tree.pack(fill="both", expand=True)

        def show_history_context(event):
            iid = tree.identify_row(event.y)
            if iid:
                tree.selection_set(iid)
                h_idx = int(tree.item(iid, "tags")[0])
                m = tk.Menu(win, tearoff=0, bg="#2e2e2e", fg="white")
                m.add_command(label="💾 Vuoi salvare nell'archivio la base? (Tasto Destro)", 
                              command=lambda: self._save_history_to_disk(h_idx))
                m.post(event.x_root, event.y_root)

        tree.bind("<Button-3>", show_history_context)
        tree.bind("<Double-Button-1>", lambda e: self._restore_from_history(tree, win))

    def _save_history_to_disk(self, history_idx):
        """Copia la base elaborata permanentemente nell'archivio"""
        item = self.mw.play_history[history_idx]
        src = item.get("processed_path")
        
        if not src or not os.path.exists(str(src)):
            messagebox.showwarning("Errore", "File elaborato non trovato o base originale non modificata.")
            return

        suggested = f"{item['song']} ({item['pitch']:+}).mp4"
        dest = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~/karaoke_clean/Basi_karaoke"),
            initialfile=suggested,
            defaultextension=".mp4",
            filetypes=[("Video MP4", "*.mp4")]
        )
        
        if dest:
            try:
                shutil.copy2(src, dest)
                messagebox.showinfo("Successo", "Base salvata nell'archivio!")
            except Exception as e:
                messagebox.showerror("Errore", f"Salvataggio fallito: {e}")

    def _restore_from_history(self, tree, win):
        """Ripristina correttamente con source e pitch"""
        sel = tree.selection()
        if not sel: return
        idx = int(tree.item(sel[0], "tags")[0])
        it = self.mw.play_history[idx]
        self.open_singer_popup(
            initial_name=it['name'], 
            initial_song=it['song'], 
            initial_source=it['source'], 
            initial_pitch=it['pitch']
        )
        win.destroy()

    def remove_singer(self):
        sel = self.mw.tree.selection()
        if sel and messagebox.askyesno("Conferma", "Vuoi rimuovere il cantante?"):
            idx = self.mw.tree.index(sel[0])
            self.mw.playlist_data.pop(idx)
            self.mw.refresh_tree()

    def change_folder(self):
        path = filedialog.askdirectory()
        if path: self.mw.scanner.scan(path)

    def save_to_archive(self):
        sel = self.mw.tree.selection()
        if sel:
            idx = self.mw.tree.index(sel[0])
            self.mw.media_logic.save_current_to_local(idx)

    # ==========================================================
    # GESTIONE MIRRORING (INTERRUTTORE BROWSER)
    # ==========================================================
    def on_mirror_click(self):
        """Gestisce l'apertura della finestra di ricerca per la cattura OBS"""
        if not self.mw.mirror_active:
            print("[SISTEMA] Apertura finestra ricerca YouTube...")
            # 1. Apre la finestra video
            self.mw.browser.launch_video("https://www.youtube.com") 
            
            # 2. Comando OBS: Stato 2 (Video ON)
            self.mw.root.after(1000, self.mw.obs.set_stato_karaoke)
            
            self.mw.mirror_active = True
            if self.mw.lbl_status:
                self.mw.lbl_status.config(text="RICERCA: APERTA (Cattura OBS)", fg="#00ff00")
        else:
            print("[SISTEMA] Chiusura finestra ricerca...")
            # 1. Comando OBS: Stato 3 (IDLE)
            self.mw.obs.set_stato_idle()
            
            # 2. Chiude il browser
            self.mw.browser.close_video() 
            
            # --- AGGIUNGI QUESTE RIGHE ---
            self.mw.mirror_active = False
            if self.mw.lbl_status:
                self.mw.lbl_status.config(text="RICERCA: CHIUSA", fg="#888888")
