import os

class Visualizer:
    def __init__(self):
        # Stato del visualizer e immagine statica persistente
        self.enabled = True
        self.bg_image = None
        
        # Preset lavfi ottimizzati: 25 FPS riducono il carico CPU del 50%
        self.presets = {
            "default": "avectorscope=s=1280x720:mode=polar:draw=line:rc=255:gc=100:bc=0:rate=25",
            "waves": "showwaves=s=1280x720:mode=line:colors=white:r=25",
            "spectrum": "showspectrum=s=1280x720:mode=combined:color=fire:fps=25",
        }

    def _is_audio_only(self, path: str) -> bool:
        """Verifica se il file è un formato audio puro."""
        if not path:
            return False
        return path.lower().endswith((".mp3", ".wav", ".flac", ".m4a"))

    def get_options(self, path: str, is_radio: bool = False, preset: str = "default"):
        """
        Restituisce la stringa di opzioni per mpv.loadfile.
        - Se attivo: genera il visualizer scelto a 25 FPS (carico CPU ridotto).
        - Se disattivo: carica l'immagine statica locale (se presente) risparmiando CPU.
        """
        if is_radio or self._is_audio_only(path):
            if self.enabled:
                filt = self.presets.get(preset, self.presets["default"])
                # [aid1]asplit separa l'audio per le casse [ao] e per il visualizer [v]
                lavfi = f"[aid1]asplit[ao][v];[v]{filt}[vo]"
                return f'lavfi-complex="{lavfi}",force-window=yes,vid=1'
            
            elif self.bg_image and os.path.exists(self.bg_image):
                # Ottimizzazione: Carica l'immagine statica come traccia video (carico CPU quasi zero)
                img_path = self.bg_image.replace("'", "\\'")
                lavfi = f"movie='{img_path}'[vo]"
                return f'lavfi-complex="{lavfi}",force-window=yes,vid=1'
            
            # Caso fallback: finestra aperta ma nera se tutto è spento
            return 'lavfi-complex="",force-window=yes'
        
        # Reset per i video normali: rimuove i filtri e chiude la finestra forzata
        return 'lavfi-complex="",force-window=no'
