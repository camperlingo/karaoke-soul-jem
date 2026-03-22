import os
import random

class Visualizer:
    def __init__(self):
        self.enabled = True
        self.bg_image = None
        self.video_folder = None
        
    def _is_audio_only(self, path: str) -> bool:
        if not path: return False
        return path.lower().endswith((".mp3", ".wav", ".flac", ".m4a"))

    def get_random_video(self, exclude=None):
        """Pesca un video casuale dalla cartella, escludendo quello attuale se possibile."""
        if not self.video_folder or not os.path.exists(self.video_folder):
            return None
        exts = (".mp4", ".mkv", ".avi", ".webm")
        videos = [f for f in os.listdir(self.video_folder) if f.lower().endswith(exts)]
        if not videos: return None
        
        # Evita di ripescare lo stesso video di fila
        if len(videos) > 1 and exclude:
            exclude_name = os.path.basename(exclude)
            videos = [v for v in videos if v != exclude_name]
            
        return os.path.join(self.video_folder, random.choice(videos))

    def get_bg_file(self, path: str, is_radio: bool = False):
        """Restituisce il percorso del file (immagine o video) da iniettare, o None."""
        if is_radio or self._is_audio_only(path):
            if self.enabled and self.video_folder and os.path.exists(self.video_folder):
                return self.get_random_video()
            elif not self.enabled and self.bg_image and os.path.exists(self.bg_image):
                return self.bg_image
        return None
