import tkinter as tk
from tkinter import ttk, messagebox

class PlaylistView:
    """
    UI della playlist cantanti.
    Gestisce il layout della colonna destra, inclusi stili e scrollbar.
    Riceve il riferimento diretto a 'mw' (MainWindow) per evitare errori di percorso.
    """

    def __init__(self, parent, mw):
        self.parent = parent
        self.mw = mw  # <--- FIX: Salviamo il riferimento sicuro alla MainWindow
        self.frame = tk.Frame(parent, bg="#121212", width=360)
        self.frame.pack(side="right", fill="y")
        self.frame.pack_propagate(False)

        # Inizializzazione stili personalizzati per la Treeview
        self._setup_styles()
        self._build()

    def _setup_styles(self):
        """Configura l'aspetto della tabella per adattarsi al tema dark."""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Treeview",
            background="#1a1a1a",
            foreground="white",
            fieldbackground="#1a1a1a",
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        
        style.configure(
            "Treeview.Heading",
            background="#333",
            foreground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold")
        )
        
        style.map("Treeview", background=[('selected', '#007acc')])
        style.map("Treeview.Heading", background=[('active', '#444')])

    def _build(self):
        """Costruisce i componenti della colonna Playlist."""
        
        # Titolo Sezione
        tk.Label(
            self.frame,
            text="PLAYLIST CANTANTI",
            bg="#121212",
            fg="yellow",
            font=("Arial", 10, "bold")
        ).pack(pady=(10, 5))

        # ---- CONTENITORE TREEVIEW + SCROLLBAR ----
        tree_container = tk.Frame(self.frame, bg="#121212")
        tree_container.pack(fill="both", expand=True, padx=5)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("name", "song", "pitch", "status"),
            show="headings",
            selectmode="browse"
        )

        # Definizione Intestazioni
        self.tree.heading("name", text="Cantante")
        self.tree.heading("song", text="Base")
        self.tree.heading("pitch", text="Pitch")
        self.tree.heading("status", text="Stato")

        # Definizione Colonne
        self.tree.column("name", width=100, anchor="w")
        self.tree.column("song", width=110, anchor="w")
        self.tree.column("pitch", width=45, anchor="center")
        self.tree.column("status", width=85, anchor="center")

        # Scrollbar Verticale
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- PULSANTI DI SPOSTAMENTO (ORDINE) ----
        move_box = tk.Frame(self.frame, bg="#121212")
        move_box.pack(fill="x", pady=8)

        self.btn_up = tk.Button(
            move_box, text="MUOVI SU ⬆", bg="#333", fg="white", 
            relief="flat", font=("Arial", 8), width=15,
            command=self.move_up # Collegato alla funzione
        )
        self.btn_up.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_down = tk.Button(
            move_box, text="MUOVI GIÙ ⬇", bg="#333", fg="white", 
            relief="flat", font=("Arial", 8), width=15,
            command=self.move_down # Collegato alla funzione
        )
        self.btn_down.pack(side="left", padx=5, expand=True, fill="x")

        # ---- PULSANTI AZIONE ----
        actions_f = tk.Frame(self.frame, bg="#121212")
        actions_f.pack(fill="x", side="bottom", pady=10)

        self.btn_add = tk.Button(
            actions_f, text="➕ AGGIUNGI CANTANTE",
            bg="#007acc", fg="white", relief="flat", font=("Arial", 9, "bold")
        )
        self.btn_add.pack(fill="x", padx=10, pady=2)

        self.btn_play = tk.Button(
            actions_f, text="▶ AVVIA ESECUZIONE",
            bg="#28a745", fg="white", relief="flat", font=("Arial", 9, "bold")
        )
        self.btn_play.pack(fill="x", padx=10, pady=2)

        self.btn_save = tk.Button(
            actions_f, text="💾 ARCHIVIA SESSIONE",
            bg="#ff9800", fg="black", relief="flat", font=("Arial", 9, "bold")
        )
        self.btn_save.pack(fill="x", padx=10, pady=2)

        self.btn_delete = tk.Button(
            actions_f, text="🗑 ELIMINA SELEZIONATO",
            bg="#c62828", fg="white", relief="flat", font=("Arial", 9),
            command=self.delete_selected # Collegato alla funzione
        )
        self.btn_delete.pack(fill="x", padx=10, pady=2)

        self.btn_toggle = tk.Button(
            actions_f, text="⏸ FERMA / RIPRENDI CODA",
            bg="#546e7a", fg="white", relief="flat", font=("Arial", 9)
        )
        self.btn_toggle.pack(fill="x", padx=10, pady=2)

        self.btn_history = tk.Button(
            actions_f, text="📜 STORICO SERATA",
            bg="#455a64", fg="white", relief="flat", font=("Arial", 9)
        )
        self.btn_history.pack(fill="x", padx=10, pady=2)

    # ==========================================================
    # LOGICA AGGIUNTA (SENZA RIMUOVERE NULLA)
    # ==========================================================

    def move_up(self):
        selected = self.tree.selection()
        if not selected: return
        item = selected[0]
        idx = self.tree.index(item)
        if idx > 0:
            # FIX: Uso self.mw diretto invece di cercare nel parent
            self.tree.move(item, '', idx - 1)
            d = self.mw.playlist_data
            d[idx], d[idx-1] = d[idx-1], d[idx]

    def move_down(self):
        selected = self.tree.selection()
        if not selected: return
        item = selected[0]
        idx = self.tree.index(item)
        total = len(self.tree.get_children())
        if idx < total - 1:
            # FIX: Uso self.mw diretto
            self.tree.move(item, '', idx + 1)
            d = self.mw.playlist_data
            d[idx], d[idx+1] = d[idx+1], d[idx]

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected: return
        item_id = selected[0]
        idx = self.tree.index(item_id)
        
        # FIX: Uso self.mw diretto
        item_data = self.mw.playlist_data[idx]
        
        if messagebox.askyesno("Conferma", f"Eliminare {item_data['name']}?"):
            if hasattr(self.mw, "processor"):
                self.mw.processor.stop_processing(item_data)
            self.mw.playlist_data.pop(idx)
            self.tree.delete(item_id)
