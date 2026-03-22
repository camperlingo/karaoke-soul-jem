import os

class PlaylistLogic:
    """
    Gestione logica playlist + diario (history)
    """

    def __init__(self, main_window):
        self.mw = main_window

        # storico cantanti eseguiti
        if not hasattr(self.mw, "play_history"):
            self.mw.play_history = []

    # ==========================================================
    # ADD TO PLAYLIST
    # ==========================================================
    def add_to_playlist(self, name, song, source, pitch):
        try:
            pitch = int(pitch)
        except Exception:
            pitch = 0

        # Pulizia input
        source = source.strip()

        item = {
            "id": os.urandom(6).hex(),
            "name": name,
            "song": song,
            "source": source,
            "pitch": pitch,
            "path": None,
            "phase": "IDLE",
            "progress": 0,
        }

        self.mw.playlist_data.append(item)
        self.mw.refresh_tree()

        # LOGICA CORRETTA:
        # Se è un URL YouTube (http) DEVE andare al processore, anche se pitch è 0.
        # Se è un file locale e pitch è 0, lo mettiamo subito come pronto.
        if int(pitch) == 0 and not source.startswith("http"):
            if os.path.exists(source):
                item["path"] = source
                item["phase"] = "DONE"
                item["progress"] = 100
                self.mw.refresh_tree()
                return

        # Altrimenti avvia il processore (che ora si chiama media_logic)
        self._start_processing(item)

    # ==========================================================
    # UPDATE / EDIT
    # ==========================================================
    def update_singer(self, index, name, song, source, pitch):
        if index >= len(self.mw.playlist_data):
            return

        item = self.mw.playlist_data[index]

        try:
            pitch = int(pitch)
        except Exception:
            pitch = 0

        source = source.strip()

        # verifica se serve rilavorare
        needs_processing = (
            source != item.get("source") or
            pitch != item.get("pitch")
        )

        item["name"] = name
        item["song"] = song
        item["source"] = source
        item["pitch"] = pitch

        if not needs_processing:
            self.mw.refresh_tree()
            return

        item["path"] = None
        item["phase"] = "IDLE"
        item["progress"] = 0
        self.mw.refresh_tree()

        self._start_processing(item)
    # ==========================================================
    # PROCESS (MODIFICATO PER MEDIA_LOGIC)
    # ==========================================================
    def _start_processing(self, item):
        """
        Invia l'elemento al MediaLogic per il download/encoding.
        """
        try:
            # Troviamo l'indice corrente dell'item per passarlo al media_logic
            idx = self.mw.playlist_data.index(item)
            
            # Usiamo il nuovo media_logic che abbiamo configurato prima
            self.mw.media_logic.start_direct_process(item["source"], item["pitch"], index=idx)
            
        except Exception as e:
            print(f"[PLAYLIST LOGIC ERROR] {e}")
            item["phase"] = "ERROR"
            item["progress"] = 0
            self.mw.refresh_tree()

    # ==========================================================
    # MOVE ORDER
    # ==========================================================
    def move_item(self, direction):
        tree = self.mw.tree
        sel = tree.selection()
        if not sel:
            return

        idx = tree.index(sel[0])
        new_idx = idx + direction

        if not (0 <= new_idx < len(self.mw.playlist_data)):
            return

        self.mw.playlist_data[idx], self.mw.playlist_data[new_idx] = (
            self.mw.playlist_data[new_idx],
            self.mw.playlist_data[idx],
        )

        self.mw.refresh_tree()

        children = tree.get_children()
        tree.selection_set(children[new_idx])
        tree.see(children[new_idx])

    # ==========================================================
    # WHEN PLAY STARTS
    # ==========================================================
    def mark_as_playing(self, index):
        if index >= len(self.mw.playlist_data):
            return

        item = self.mw.playlist_data[index]
        self.mw.play_history.append(item.copy())
        del self.mw.playlist_data[index]
        self.mw.refresh_tree()
