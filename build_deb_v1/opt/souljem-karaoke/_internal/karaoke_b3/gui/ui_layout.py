import tkinter as tk
from tkinter import ttk

class UILayout:
    """
    Responsabile della costruzione grafica e della gestione dei riferimenti ai widget.
    Versione ottimizzata per il modulo MainWindow.
    """

    def __init__(self, root):
        self.root = root

        # --- Riferimenti Colonne Principali ---
        self.col_left = None
        self.col_center = None
        self.col_right = None

        # --- Widget Archivio (Sinistra) ---
        self.lsb_files = None
        self.ent_search = None
        self.btn_change_folder = None

        # --- Widget Video e Radio (Centro) ---
        self.v_frame = None
        self.radio_box = None  
        self.ent_bg_url = None
        self.btn_browse_bg = None
        self.btn_radio_play = None
        self.btn_radio_toggle = None
        # --- PATCH: Riferimenti nuovi pulsanti Radio ---
        self.btn_viz_toggle = None
        self.btn_radio_img = None
        self.vol_bg = None
        
        # --- Indicatori di Progresso ---
        self.prog_main = None
        self.prog_radio = None

        # --- Controlli Player ---
        self.slider = None
        self.slider_var = None
        self.vol_main = None
        self.btn_play_pause = None
        self.btn_stop = None
        self.btn_sala = None
        self.btn_mirror = None

        # --- Inserimento Rapido ---
        self.ent_quick_url = None
        self.btn_quick_load = None

        # --- Switcher e Status ---
        self.btn_toggle_archive = None
        self.btn_toggle_playlist = None
        self.lbl_status = None

    def _setup_right_click(self, widget):
        """Aggiunge il menu contestuale standard (Taglia/Copia/Incolla)."""
        menu = tk.Menu(widget, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#007acc")
        menu.add_command(label="Taglia", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copia", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Incolla", command=lambda: widget.event_generate("<<Paste>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        
        widget.bind("<Button-3>", show_menu)

    def build(self):
        """Esegue il build sequenziale dell'interfaccia."""
        # Configurazione pesi per il ridimensionamento
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._build_left_column()
        self._build_center_column()
        self._build_right_column()
        self._build_status_bar()

    def _build_left_column(self):
        """Costruisce la colonna dell'archivio locale con funzione Refresh."""
        self.col_left = tk.Frame(self.root, bg="#121212", width=260)
        self.col_left.pack(side="left", fill="y")
        self.col_left.pack_propagate(False)

        tk.Label(
            self.col_left, text="ARCHIVIO BASI",
            bg="#121212", fg="#888", font=("Arial", 10, "bold")
        ).pack(pady=(10, 5))

        # Campo Ricerca
        search_frame = tk.Frame(self.col_left, bg="#121212")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        self.ent_search = tk.Entry(
            search_frame, bg="#1e1e1e", fg="white", 
            insertbackground="white", borderwidth=0
        )
        self.ent_search.pack(fill="x", ipady=3)
        self._setup_right_click(self.ent_search)

        # Listbox File
        self.lsb_files = tk.Listbox(
            self.col_left, bg="#0d0d0d", fg="#ccc",
            font=("Segoe UI", 10), borderwidth=0, 
            highlightthickness=1, highlightbackground="#333",
            selectbackground="#007acc"
        )
        self.lsb_files.pack(fill="both", expand=True, padx=10, pady=5)

        # Pulsantiere Inferiore (Aggiorna + Cambia Cartella)
        btn_box = tk.Frame(self.col_left, bg="#121212")
        btn_box.pack(fill="x", pady=10, padx=10)

        # Pulsante Aggiorna (NUOVO)
        self.btn_refresh = tk.Button(
            btn_box, text="🔄", 
            bg="#444", fg="white", relief="flat", width=3,
            font=("Arial", 10, "bold")
        )
        self.btn_refresh.pack(side="left", padx=(0, 5))

        # Pulsante Cartella
        self.btn_change_folder = tk.Button(
            btn_box, text="📁 CAMBIA CARTELLA",
            bg="#333", fg="white", relief="flat", overrelief="raised"
        )
        self.btn_change_folder.pack(side="left", fill="x", expand=True)

    def _build_center_column(self):
        """Area centrale: Video, Controlli e Radio."""
        self.col_center = tk.Frame(self.root, bg="#000")
        self.col_center.pack(side="left", fill="both", expand=True)

        # --- SEZIONE RADIO / DUCKING ---
        self.radio_box = tk.LabelFrame(
            self.col_center, text="RADIO & BACKGROUND CONTROLS",
            bg="#121212", fg="cyan", font=("Arial", 9, "bold"), labelanchor="n"
        )
        self.radio_box.pack(fill="x", padx=10, pady=5)

        # Input Radio
        in_radio = tk.Frame(self.radio_box, bg="#121212")
        in_radio.pack(fill="x", padx=5, pady=5)

        self.ent_bg_url = tk.Entry(
            in_radio, bg="#1e1e1e", fg="#00ff00", 
            insertbackground="white", font=("Consolas", 10), borderwidth=0
        )
        self.ent_bg_url.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=2)
        self._setup_right_click(self.ent_bg_url)

        self.btn_browse_bg = tk.Button(in_radio, text="📁", width=3, bg="#444", fg="white", relief="flat")
        self.btn_browse_bg.pack(side="right")

        # Pulsanti Radio
        btn_radio_f = tk.Frame(self.radio_box, bg="#121212")
        btn_radio_f.pack(fill="x", padx=5, pady=2)

        self.btn_radio_play = tk.Button(btn_radio_f, text="CARICA SOTTOFONDO", bg="#005a9e", fg="white", relief="flat")
        self.btn_radio_play.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_radio_toggle = tk.Button(btn_radio_f, text="PLAY/PAUSA RADIO", bg="#3c3c3c", fg="white", relief="flat")
        self.btn_radio_toggle.pack(side="left", fill="x", expand=True, padx=2)
        
        # --- PATCH: NUOVI PULSANTI VIZ E IMAGE ---
        self.btn_viz_toggle = tk.Button(btn_radio_f, text="VIZ ON", bg="#5e35b1", fg="white", relief="flat", font=("Arial", 8, "bold"), width=10)
        self.btn_viz_toggle.pack(side="left", padx=2)

        self.btn_radio_img = tk.Button(btn_radio_f, text="JPG/PNG", bg="#f57c00", fg="white", relief="flat", font=("Arial", 8, "bold"), width=10)
        self.btn_radio_img.pack(side="left", padx=2)

        # Dashboard Radio (Volumi e Progress)
        dash = tk.Frame(self.radio_box, bg="#121212")
        dash.pack(fill="x", padx=5, pady=10)

        tk.Label(dash, text="VOL", bg="#121212", fg="#888", font=("Arial", 7)).pack(side="left")
        self.vol_bg = ttk.Scale(dash, from_=0, to=100, orient="horizontal", length=80)
        self.vol_bg.set(40)
        self.vol_bg.pack(side="left", padx=5)

        tk.Label(dash, text="MAIN SYNC", bg="#121212", fg="cyan", font=("Arial", 7, "bold")).pack(side="left", padx=(10, 0))
        self.prog_main = ttk.Progressbar(dash, orient="horizontal", mode="determinate", length=120)
        self.prog_main.pack(side="left", padx=5)

        tk.Label(dash, text="RADIO", bg="#121212", fg="#00ff00", font=("Arial", 7, "bold")).pack(side="left", padx=(10, 0))
        self.prog_radio = ttk.Progressbar(dash, orient="horizontal", mode="determinate", length=120)
        self.prog_radio.pack(side="left", padx=5)

        # --- VIDEO FRAME ---
        self.v_frame = tk.Frame(self.col_center, bg="black", highlightbackground="#222", highlightthickness=1)
        self.v_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- CONTROLLI INFERIORI ---
        bottom = tk.Frame(self.col_center, bg="#121212")
        bottom.pack(fill="x", side="bottom")

        # Avanzamento
        self.slider_var = tk.DoubleVar()
        self.slider = ttk.Scale(bottom, from_=0, to=100, variable=self.slider_var, orient="horizontal")
        self.slider.pack(fill="x", padx=15, pady=5)

        # Quick Load Area
        quick = tk.Frame(bottom, bg="#121212")
        quick.pack(fill="x", padx=15, pady=5)

        self.ent_quick_url = tk.Entry(quick, bg="#1e1e1e", fg="#00ffff", font=("Consolas", 10), borderwidth=0)
        self.ent_quick_url.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=2)
        self._setup_right_click(self.ent_quick_url)

        self.btn_quick_load = tk.Button(quick, text="LOAD / BROWSE", bg="#007acc", fg="white", font=("Arial", 8, "bold"), relief="flat")
        self.btn_quick_load.pack(side="right")

        # Toolbar Principale
        ctrl = tk.Frame(bottom, bg="#121212")
        ctrl.pack(fill="x", pady=(5, 15), padx=10)

        self.btn_toggle_archive = tk.Button(ctrl, text="◀|▶", bg="#333", fg="white", width=4, relief="flat")
        self.btn_toggle_archive.pack(side="left", padx=2)

        self.btn_sala = tk.Button(ctrl, text="SALA OFF", bg="#444", fg="white", height=2, width=12, font=("Arial", 9, "bold"))
        self.btn_sala.pack(side="left", padx=5)

        self.btn_mirror = tk.Button(ctrl, text="🪞 MIRROR", bg="#3949ab", fg="white", height=2, width=10)
        self.btn_mirror.pack(side="left", padx=5)

        tk.Label(ctrl, text="VOL", bg="#121212", fg="white", font=("Arial", 8)).pack(side="left", padx=2)
        self.vol_main = ttk.Scale(ctrl, from_=0, to=100, orient="horizontal", length=100)
        self.vol_main.set(100)
        self.vol_main.pack(side="left", padx=5)

        self.btn_play_pause = tk.Button(ctrl, text="▶ PLAY", bg="#28a745", fg="white", height=2, font=("Arial", 10, "bold"))
        self.btn_play_pause.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = tk.Button(ctrl, text="STOP", bg="#dc3545", fg="white", height=2, width=10)
        self.btn_stop.pack(side="left", padx=5)

        self.btn_toggle_playlist = tk.Button(ctrl, text="▶|◀", bg="#333", fg="white", width=4, relief="flat")
        self.btn_toggle_playlist.pack(side="right", padx=2)

    def _build_right_column(self):
        """Prepara lo spazio per la colonna Playlist."""
        self.col_right = tk.Frame(self.root, bg="#121212", width=380)
        self.col_right.pack(side="right", fill="y")
        self.col_right.pack_propagate(False)

    def _build_status_bar(self):
        """Barra di stato inferiore per feedback immediato."""
        self.lbl_status = tk.Label(
            self.root, text="SISTEMA PRONTO",
            bg="#002244", fg="cyan", relief="flat", 
            font=("Consolas", 9), anchor="w", padx=10
        )
        self.lbl_status.pack(side="bottom", fill="x")
