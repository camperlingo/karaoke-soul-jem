import subprocess
import os
# IMPORT CORRETTO
from karaoke_b3.core.logger import info

class BrowserController:
    def __init__(self):
        self.profile = os.path.expanduser("~/karaoke_video_instance")
        self.process = None

    def launch_video(self, url):
        """STATO 2: Apre l'unica finestra video per OBS."""
        self.close_video()
        flags = [
            "chromium",
            f"--user-data-dir={self.profile}",
            "--new-window",
            "--no-first-run",
            "--app=" + url,
            "--start-maximized"
        ]
        self.process = subprocess.Popen(flags)
        info(f"[BROWSER] Video lanciato: {url}")

    def close_video(self):
        if self.process:
            self.process.terminate()
            self.process = None
        os.system(f"pkill -9 -f {self.profile}")
