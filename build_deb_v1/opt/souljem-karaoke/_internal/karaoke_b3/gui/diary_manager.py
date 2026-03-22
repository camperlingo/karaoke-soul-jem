import json
import os
import time
import uuid


class DiaryManager:
    """
    Gestisce il diario persistente delle esecuzioni.
    NON modifica playlist.
    NON lancia player.
    NON processa file.
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.expanduser("~/karaoke_clean")

        self.dir = base_dir
        self.path = os.path.join(self.dir, "diario.json")

        os.makedirs(self.dir, exist_ok=True)
        self._data = []

        self._load()

    # --------------------------------------------------
    # LOAD / SAVE
    # --------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = []
        else:
            self._data = []

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # --------------------------------------------------
    # API PUBBLICA
    # --------------------------------------------------
    def add(self, item: dict):
        """
        Aggiunge una voce al diario.
        """
        entry = {
            "id": uuid.uuid4().hex,
            "timestamp": int(time.time()),
            "name": item.get("name"),
            "song": item.get("song"),
            "source": item.get("source"),
            "path": item.get("path"),
            "pitch": item.get("pitch", 0),
        }

        self._data.append(entry)
        self._save()

    def list(self):
        """Ritorna tutte le voci (ordine cronologico)"""
        return list(self._data)

    def clear(self):
        self._data = []
        self._save()

    def remove(self, entry_id):
        self._data = [x for x in self._data if x.get("id") != entry_id]
        self._save()

