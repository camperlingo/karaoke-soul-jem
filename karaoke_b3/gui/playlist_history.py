import tkinter as tk
from tkinter import ttk
import time


class PlaylistHistory:
    """
    Diario cantanti:
    - mantiene traccia dei brani eseguiti
    - permette di reinserirli in playlist
    """

    def __init__(self, main_window):
        self.mw = main_window
        self.items = []

    # ==========================================================
    # ADD ENTRY
    # ==========================================================
    def add(self, item: dict):
        entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "name": item.get("name", ""),
            "song": item.get("song", ""),
            "source": item.get("source"),
            "pitch": item.get("pitch", 0),
            "path": item.get("path"),
        }
        self.items.append(entry)

    # ==========================================================
    # OPEN WINDOW
    # ==========================================================
    def open_window(self):
        win = tk.Toplevel(self.mw.root)
        win.title("📜 Diario Cantanti")
        win.geometry("720x420")
        win.configure(bg="#121212")

        tree = ttk.Treeview(
            win,
            columns=("time", "name", "song", "pitch"),
            show="headings"
        )

        tree.heading("time", text="Ora")
        tree.heading("name", text="Cantante")
        tree.heading("song", text="Base")
        tree.heading("pitch", text="Pitch")

        tree.column("time", width=80)
        tree.column("name", width=160)
        tree.column("song", width=320)
        tree.column("pitch", width=60, anchor="center")

        tree.pack(fill="both", expand=True, padx=6, pady=6)

        for item in self.items:
            tree.insert(
                "",
                "end",
                values=(
                    item["timestamp"],
                    item["name"],
                    item["song"],
                    f"{item['pitch']:+}"
                )
            )

        tree.bind(
            "<Double-Button-1>",
            lambda e: self._restore_from_history(tree)
        )

    # ==========================================================
    # RESTORE → popup cantante
    # ==========================================================
    def _restore_from_history(self, tree):
        sel = tree.selection()
        if not sel:
            return

        idx = tree.index(sel[0])
        if idx >= len(self.items):
            return

        item = self.items[idx]

        # richiama popup standard
        self.mw.actions.open_singer_popup(
            initial_name=item.get("name", ""),
            initial_song=item.get("song", ""),
            initial_source=item.get("source", ""),
            initial_pitch=item.get("pitch", 0)
        )

