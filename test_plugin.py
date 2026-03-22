import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Configurazione base
DEFAULT_DIR = os.path.expanduser("~/karaoke_clean/MP3_DOWNLOADS")
os.makedirs(DEFAULT_DIR, exist_ok=True)

class SuperDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HQ Studio Downloader (Plugin Test)")
        # Finestra molto più compatta per i notebook!
        self.root.geometry("680x620") 
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("green.Horizontal.TProgressbar", foreground='#4CAF50', background='#4CAF50')

        self.current_search_results = []

        self.setup_ui()
        self.abilita_tasto_destro()

    def abilita_tasto_destro(self):
        self.menu_mouse = tk.Menu(self.root, tearoff=0)
        self.menu_mouse.add_command(label="Taglia", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        self.menu_mouse.add_command(label="Copia", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        self.menu_mouse.add_command(label="Incolla", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))

        def mostra_menu(e):
            if isinstance(e.widget, tk.Entry):
                e.widget.focus()
                self.menu_mouse.tk_popup(e.x_root, e.y_root)

        self.root.bind_class("Entry", "<Button-3>", mostra_menu)

    def setup_ui(self):
        # Margini ridotti al minimo
        main_frame = tk.Frame(self.root, padx=15, pady=5)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="🎛️ STUDIO DOWNLOADER HQ", font=("Arial", 14, "bold"), fg="#2196F3").pack(pady=(0, 5))

        # --- 0. RICERCA INTEGRATA ---
        frame_search = tk.LabelFrame(main_frame, text=" 🔍 Ricerca Rapida YouTube ", font=("Arial", 9, "bold"), pady=5, padx=10, fg="#ffcc00", bg="#2b2b2b")
        frame_search.pack(fill="x", pady=2)
        
        s_box = tk.Frame(frame_search, bg="#2b2b2b")
        s_box.pack(fill="x")
        self.search_entry = tk.Entry(s_box, font=("Arial", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=2)
        self.search_entry.bind("<Return>", lambda e: self.esegui_ricerca())
        
        self.btn_cerca_yt = tk.Button(s_box, text="Cerca", command=self.esegui_ricerca, bg="#ff9800", fg="black", font=("Arial", 9, "bold"))
        self.btn_cerca_yt.pack(side="left", padx=5)

        # Altezza lista ridotta (3 righe bastano per far vedere che ci sono risultati)
        self.list_results = tk.Listbox(frame_search, height=4, font=("Arial", 9), bg="#1e1e1e", fg="white", selectbackground="#2196F3")
        self.list_results.pack(fill="x", pady=(5, 0))
        tk.Label(frame_search, text="Fai doppio clic su un risultato per caricarlo giù 👇", font=("Arial", 8, "italic"), bg="#2b2b2b", fg="#aaa").pack()
        self.list_results.bind("<Double-1>", self.seleziona_risultato)

        # --- 1. CARTELLA E IMPOSTAZIONI SULLA STESSA RIGA PER RISPARMIARE SPAZIO ---
        frame_mid = tk.Frame(main_frame)
        frame_mid.pack(fill="x", pady=5)

        tk.Label(frame_mid, text="Salva in:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.folder_var = tk.StringVar(value=DEFAULT_DIR)
        tk.Entry(frame_mid, textvariable=self.folder_var, bg="#f0f0f0", width=55).grid(row=0, column=1, padx=5, ipady=2)
        tk.Button(frame_mid, text="📂 Scegli", command=self.scegli_cartella).grid(row=0, column=2)

        # --- 2. PARAMETRI AUDIO ---
        frame_opt = tk.Frame(main_frame)
        frame_opt.pack(fill="x", pady=5)

        tk.Label(frame_opt, text="Fmt:").pack(side="left")
        self.fmt_var = tk.StringVar(value="mp3")
        ttk.Combobox(frame_opt, textvariable=self.fmt_var, values=["mp3", "m4a", "flac", "wav"], width=5, state="readonly").pack(side="left", padx=5)

        tk.Label(frame_opt, text="Bitrate:").pack(side="left")
        self.bitrate_var = tk.StringVar(value="320")
        ttk.Combobox(frame_opt, textvariable=self.bitrate_var, values=["320", "256", "192", "VBR (Auto)"], width=10, state="readonly").pack(side="left", padx=5)

        tk.Label(frame_opt, text="Hz:").pack(side="left")
        self.hz_var = tk.StringVar(value="48000")
        ttk.Combobox(frame_opt, textvariable=self.hz_var, values=["48000", "44100"], width=7, state="readonly").pack(side="left", padx=5)

        # --- 3. URL E NOME FILE ---
        tk.Label(main_frame, text="Link YouTube:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
        url_box = tk.Frame(main_frame)
        url_box.pack(fill="x")
        self.url_entry = tk.Entry(url_box, font=("Arial", 10))
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=2)
        self.btn_cerca_titolo = tk.Button(url_box, text="🔄 Info", command=self.ottieni_titolo, bg="#2196F3", fg="white", font=("Arial", 8, "bold"))
        self.btn_cerca_titolo.pack(side="left", padx=5)

        tk.Label(main_frame, text="Nome File (senza .mp3):", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
        self.name_entry = tk.Entry(main_frame, font=("Arial", 10), fg="#333")
        self.name_entry.pack(fill="x", ipady=2)

        # --- 4. DOWNLOAD E PROGRESSO ---
        self.btn_scarica = tk.Button(main_frame, text="⬇ SCARICA ORA", bg="#cccccc", fg="black", font=("Arial", 12, "bold"), command=self.scarica, state="disabled", height=1)
        self.btn_scarica.pack(fill="x", pady=10)

        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill="x")
        self.percent_label = tk.Label(progress_frame, text="0%", font=("Arial", 16, "bold"), fg="#4CAF50")
        self.percent_label.pack()
        self.progress = ttk.Progressbar(progress_frame, length=500, mode='determinate', style="green.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=2)
        self.status_label = tk.Label(progress_frame, text="In attesa del link...", font=("Arial", 9), fg="#555")
        self.status_label.pack()

    # ================= LOGICA RICERCA INTERNA =================
    def esegui_ricerca(self):
        query = self.search_entry.get().strip()
        if not query: return
        
        self.btn_cerca_yt.config(state="disabled", text="Ricerco...")
        self.list_results.delete(0, tk.END)
        self.list_results.insert(tk.END, "Sto cercando su YouTube... attendi!")
        
        def worker():
            try:
                ydl_opts = {'extract_flat': True, 'quiet': True, 'no_warnings': True, 'ignoreerrors': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch10:{query}", download=False)
                    entries = info.get('entries', [])
                self.root.after(0, lambda: self._mostra_risultati(entries))
            except Exception as e:
                self.root.after(0, lambda: self._errore_ricerca(str(e)))
                
        threading.Thread(target=worker, daemon=True).start()

    def _mostra_risultati(self, entries):
        self.btn_cerca_yt.config(state="normal", text="Cerca")
        self.list_results.delete(0, tk.END)
        self.current_search_results = []
        
        for e in entries:
            if not e: continue
            titolo = e.get('title', 'Sconosciuto')
            durata = e.get('duration', 0)
            url = e.get('url', '')
            
            # Formattiamo i minuti e secondi (Risolto bug float!)
            m, s = divmod(int(durata or 0), 60)
            testo_lista = f"[{m}:{s:02d}] - {titolo}"
            
            self.list_results.insert(tk.END, testo_lista)
            self.current_search_results.append((titolo, url))
            
        if not self.current_search_results:
            self.list_results.insert(tk.END, "Nessun risultato trovato.")

    def _errore_ricerca(self, msg):
        self.btn_cerca_yt.config(state="normal", text="Cerca")
        self.list_results.delete(0, tk.END)
        self.list_results.insert(tk.END, "Errore di connessione a YouTube.")

    def seleziona_risultato(self, event):
        selection = self.list_results.curselection()
        if not selection: return
        
        idx = selection[0]
        titolo, url = self.current_search_results[idx]
        
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        
        titolo_pulito = "".join([c for c in titolo if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
        self._imposta_titolo(titolo_pulito)

    # ================= ALTRA LOGICA =================
    def scegli_cartella(self):
        d = filedialog.askdirectory()
        if d: self.folder_var.set(d)

    def ottieni_titolo(self):
        url = self.url_entry.get().strip()
        if not url: return

        self.btn_cerca_titolo.config(state="disabled")
        self.status_label.config(text="⏳ Analisi del link in corso...", fg="blue")
        
        def worker():
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    titolo = info.get('title', 'Video_senza_titolo')
                    titolo = "".join([c for c in titolo if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                    self.root.after(0, lambda t=titolo: self._imposta_titolo(t))
            except Exception as e:
                self.root.after(0, lambda m=str(e): self._errore_titolo(m))

        threading.Thread(target=worker, daemon=True).start()

    def _imposta_titolo(self, titolo):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, titolo)
        self.status_label.config(text="✅ Brano caricato! Scegli la qualità e clicca su SCARICA ORA.", fg="green")
        self.btn_scarica.config(state="normal", bg="#4CAF50", fg="white")
        self.btn_cerca_titolo.config(state="normal")

    def _errore_titolo(self, msg):
        self.status_label.config(text="⚠️ Impossibile leggere il titolo, scrivilo a mano!", fg="orange")
        self.btn_scarica.config(state="normal", bg="#4CAF50", fg="white")
        self.btn_cerca_titolo.config(state="normal")

    def scarica(self):
        url = self.url_entry.get().strip()
        nome_file = self.name_entry.get().strip()
        folder = self.folder_var.get()
        fmt = self.fmt_var.get()
        hz = self.hz_var.get()
        bitrate = self.bitrate_var.get()
        
        if not url or not nome_file: return

        self.btn_scarica.config(state="disabled", bg="#cccccc")
        self.btn_cerca_titolo.config(state="disabled")
        self.progress["value"] = 0
        self.percent_label.config(text="0%")
        self.status_label.config(text="🚀 Avvio download...", fg="blue")

        def worker():
            try:
                ff_args = ['-ar', hz] 
                quality_val = '320' 
                if fmt in ['mp3', 'm4a']:
                    if bitrate == "VBR (Auto)":
                        ff_args.extend(['-q:a', '0']) 
                        quality_val = '0' 
                    else:
                        quality_val = bitrate

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(folder, f"{nome_file}.%(ext)s"),
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': True,
                    'nocolor': True, # Muro contro i colori ANSI (il bug del 9471%)
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': fmt,
                        'preferredquality': quality_val,
                    }],
                    'postprocessor_args': ff_args,
                    'progress_hooks': [self.update_bar],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.root.after(0, self.finish_success)
            except Exception as e:
                self.root.after(0, lambda m=str(e): self.finish_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def update_bar(self, d):
        if d['status'] == 'downloading':
            try:
                # ORA CALCOLIAMO LA PERCENTUALE USANDO I BYTE REALI!
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                
                if total > 0:
                    val = (downloaded / total) * 100
                else:
                    # Piano B se yt-dlp non ci dice i byte
                    import re
                    p = d.get('_percent_str', '0%')
                    p = re.sub(r'\x1b[^m]*m', '', p) # Pialla via i colori ANSI
                    p = ''.join(c for c in p if c.isdigit() or c == '.') 
                    val = float(p) if p else 0.0

                self.root.after(0, lambda: self.progress.config(value=val))
                self.root.after(0, lambda: self.percent_label.config(text=f"{val:.1f}%"))
                self.root.after(0, lambda: self.status_label.config(text="⬇️ Scaricamento file in corso...", fg="orange"))
            except: pass
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.percent_label.config(text="100%"))
            self.root.after(0, lambda: self.status_label.config(text="⚙️ ESTRAZIONE AUDIO HQ IN CORSO...\n(FFmpeg sta lavorando, attendi!)", fg="red"))

    def finish_success(self):
        self.status_label.config(text="✅ TUTTO FATTO! File pronto in archivio.", fg="green")
        self.percent_label.config(text="COMPLETATO")
        messagebox.showinfo("Successo", "Traccia scaricata e convertita con successo!")
        self.reset_ui()

    def finish_error(self, msg):
        self.status_label.config(text="❌ Errore durante il processo.", fg="red")
        messagebox.showerror("Errore", f"Dettagli:\n{msg}")
        self.reset_ui()

    def reset_ui(self):
        self.btn_scarica.config(state="disabled", bg="#cccccc")
        self.btn_cerca_titolo.config(state="normal")
        self.url_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperDownloaderApp(root)
    root.mainloop()