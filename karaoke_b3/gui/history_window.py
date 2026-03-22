import tkinter as tk
from tkinter import ttk


class HistoryWindow:
    """
    Finestra DIARIO CANTANTI
    Mostra tutto ciò che è stato eseguito.
    Permette di reinserire una voce in playlist.
    """

    def __init__(self, main_window):
        self.mw = main_window

        self.win = tk.Toplevel(self.mw.root)
        self.win.title("Diario Cantanti")
        self.win.geometry("700x420")
        self.win.configure(bg="#121212")

        self._build_ui()
        self._load_history()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _build_ui(self):
        title = tk.Label(
            self.win,
            text="DIARIO CANTANTI",
            bg="#121212",
            fg="cyan",
            font=("Arial", 11, "bold"),
        )
        title.pack(pady=6)

        self.tree = ttk.Treeview(
            self.win,
            columns=("name", "song", "pitch"),
            show="headings",
            height=14
        )

        self.tree.heading("name", text="Cantante")
        self.tree.heading("song", text="Base")
        self.tree.heading("pitch", text="Pitch")

        self.tree.column("name", width=200)
        self.tree.column("song", width=320)
        self.tree.column("pitch", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=8, pady=6)

        self.tree.bind("<Double-Button-1>", self._restore_selected)

        btns = tk.Frame(self.win, bg="#121212")
        btns.pack(fill="x", pady=6)

        tk.Button(
            btns,
            text="➕ Rimetti in playlist",
            command=self._restore_selected,
            bg="#007acc",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            btns,
            text="Chiudi",
            command=self.win.destroy,
            bg="#444",
            fg="white"
        ).pack(side="right", padx=5)

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    def _load_history(self):
        self.tree.delete(*self.tree.get_children())

        for item in self.mw.play_history:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    item.get("name", ""),
                    item.get("song", ""),
                    f"{item.get('pitch', 0):+}"
                )
            )

    # --------------------------------------------------
    # RESTORE
    # --------------------------------------------------
    def _restore_selected(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return

        idx = self.tree.index(sel[0])
        if idx >= len(self.mw.play_history):
            return

        item = self.mw.play_history[idx]

        # richiama popup standard (stessa logica della playlist)
        self.mw.actions.open_singer_popup(
            initial_name=item.get("name", ""),
            initial_song=item.get("song", ""),
            initial_source=item.get("source", ""),
            initial_pitch=item.get("pitch", 0),
        )

