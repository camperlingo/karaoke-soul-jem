import tkinter as tk
from tkinter import ttk, filedialog
import os

class SingerPopup:
    def __init__(self, parent, callback, initial_name="", initial_song="", initial_source="", initial_pitch=0):
        """
        Popup per la configurazione del cantante e del brano.
        Gestisce l'inserimento manuale, URL YouTube e file locali.
        """
        self.callback = callback
        self.pop = tk.Toplevel(parent)
        self.pop.title("Configurazione Brano")
        self.pop.geometry("500x550")
        self.pop.configure(bg='#1e1e1e')
        
        # --- PATCH ANTI-CRASH: Gestione chiusura manuale "X" ---
        self.pop.protocol("WM_DELETE_WINDOW", self._on_close)
        # -------------------------------------------------------
        
        # Rende il popup modale (blocca l'interazione con la finestra principale)
        self.pop.transient(parent)
        self.pop.wait_visibility()
        self.pop.grab_set()

        self.pitch_var = tk.IntVar(value=initial_pitch)
        self._build_ui(initial_name, initial_song, initial_source)

    def _on_close(self):
        """Gestisce la chiusura sicura del popup quando si preme la X"""
        try:
            self.pop.grab_release()  # Rilascia il blocco modale
            self.pop.destroy()       # Distrugge la finestra
        except:
            pass # Se è già distrutta, ignora

    def _enable_right_click(self, entry):
        """Abilita il menu contestuale per facilitare Incolla da YouTube"""
        menu = tk.Menu(entry, tearoff=0, bg="#333", fg="white")
        menu.add_command(label="Taglia", command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copia", command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Incolla", command=lambda: entry.event_generate("<<Paste>>"))
        
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        entry.bind("<Button-3>", show_menu)

    def _build_ui(self, n, s, src):
        """Costruisce i widget grafici"""
        frame = tk.Frame(self.pop, bg='#1e1e1e', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # --- SEZIONE NOME ---
        tk.Label(frame, text="NOME CANTANTE", bg='#1e1e1e', fg='white', font=('Arial', 9, 'bold')).pack(pady=(10,0))
        self.en_name = tk.Entry(frame, bg='#333', fg='white', insertbackground='white', font=('Arial', 10))
        self.en_name.pack(fill='x', pady=5)
        self.en_name.insert(0, n)
        self._enable_right_click(self.en_name)

        # --- SEZIONE TITOLO ---
        tk.Label(frame, text="TITOLO BRANO", bg='#1e1e1e', fg='white', font=('Arial', 9, 'bold')).pack(pady=(10,0))
        self.en_song = tk.Entry(frame, bg='#333', fg='white', insertbackground='white', font=('Arial', 10))
        self.en_song.pack(fill='x', pady=5)
        self.en_song.insert(0, s)
        self._enable_right_click(self.en_song)

        # --- SEZIONE SORGENTE ---
        tk.Label(frame, text="FILE LOCALE O URL YOUTUBE", bg='#1e1e1e', fg='white', font=('Arial', 9, 'bold')).pack(pady=(10,0))
        f_row = tk.Frame(frame, bg='#1e1e1e')
        f_row.pack(fill='x', pady=5)
        self.en_src = tk.Entry(f_row, bg='#333', fg='yellow', insertbackground='white', font=('Arial', 10))
        self.en_src.pack(side='left', fill='x', expand=True)
        self.en_src.insert(0, src)
        self._enable_right_click(self.en_src)
        
        tk.Button(f_row, text="📁", command=self._browse, bg='#444', fg='white', width=3).pack(side='right', padx=5)

        # --- SEZIONE PITCH ---
        tk.Label(frame, text="VARIAZIONE TONALITÀ (PITCH)", bg='#1e1e1e', fg='orange', font=('Arial', 9, 'bold')).pack(pady=15)
        p_row = tk.Frame(frame, bg='#1e1e1e')
        p_row.pack()
        
        tk.Button(p_row, text="-", command=self._pitch_down, width=5, bg='#444', fg='white').pack(side='left', padx=5)
        tk.Label(p_row, textvariable=self.pitch_var, bg='#000', fg='yellow', font=('Arial', 16, 'bold'), width=4).pack(side='left')
        tk.Button(p_row, text="+", command=self._pitch_up, width=5, bg='#444', fg='white').pack(side='left', padx=5)

        # --- SEZIONE AZIONI ---
        btn_f = tk.Frame(frame, bg='#1e1e1e')
        btn_f.pack(side='bottom', fill='x', pady=20)
        
        tk.Button(btn_f, text="🎤 AGGIUNGI A PLAYLIST", bg='#28a745', fg='white', font=('Arial', 10, 'bold'), height=2,
                  command=lambda: self._confirm("karaoke")).pack(side='left', fill='x', expand=True, padx=5)
        
        tk.Button(btn_f, text="🎹 PIANO BAR (AVVIA ORA)", bg='#007acc', fg='white', font=('Arial', 10, 'bold'), height=2,
                  command=lambda: self._confirm("pianobar")).pack(side='left', fill='x', expand=True, padx=5)

    # ==========================================================
    # LOGICA FUNZIONALE
    # ==========================================================
    def _pitch_up(self):
        self.pitch_var.set(self.pitch_var.get() + 1)

    def _pitch_down(self):
        self.pitch_var.set(self.pitch_var.get() - 1)

    def _browse(self):
        """Apertura selettore file con focus sul titolo se il file è locale"""
        f = filedialog.askopenfilename()
        if f: 
            self.en_src.delete(0, tk.END)
            self.en_src.insert(0, f)
            # Se il titolo è vuoto, inseriamo il nome del file come suggerimento
            if not self.en_song.get():
                base = os.path.basename(f).rsplit('.', 1)[0]
                self.en_song.insert(0, base)

    def _confirm(self, mode):
        """Invia i dati ripuliti alla finestra principale in sicurezza"""
        name = self.en_name.get().strip() or "Sconosciuto"
        song = self.en_song.get().strip() or "Brano Senza Titolo"
        source = self.en_src.get().strip()
        pitch = self.pitch_var.get()
        
        if not source:
            self.en_src.configure(highlightbackground="red", highlightthickness=2)
            return

        # 1. Eseguiamo il callback (Aggiungi a playlist) MENTRE la finestra esiste ancora
        self.callback(name, song, source, pitch, mode)

        # 2. Chiudiamo la finestra con un MICRO-RITARDO (50ms)
        # Questo permette all'evento "Click del Mouse" di terminare prima che la finestra sparisca
        # Prevenendo l'errore BadWindow X_QueryTree su Linux
        self.pop.after(50, self._on_close)
