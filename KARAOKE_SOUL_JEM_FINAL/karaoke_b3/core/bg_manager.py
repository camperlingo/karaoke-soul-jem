import mpv
import os
import random
import threading
import time

class BackgroundManager:
    def __init__(self, main_window=None):
        self.mw = main_window 
        self.player = mpv.MPV(
            audio_display="no", 
            vo="null", 
            volume=40, 
            force_window="no",
            ytdl=True,
            hwdec="auto-safe",
            vd_lavc_fast=True
        )
        self.playlist = []
        self.is_playing = False
        self.random_mode = True
        self.base_volume = 40 
        self.is_ducked = False 

        @self.player.property_observer('idle-active')
        def on_idle(name, value):
            if value and self.is_playing:
                threading.Thread(target=self.next, daemon=True).start()

    def set_volume(self, value):
        try:
            self.base_volume = int(float(value))
            target = 5 if self.is_ducked else self.base_volume
            
            # Applica al player principale se attivo
            if self.mw and hasattr(self.mw, 'player'):
                self.mw.player.set_volume(target)
            
            # Applica al player interno
            self.player.volume = target
        except: pass

    def load_path(self, path):
        if not path: return
        new_playlist = []
        if path.startswith("http"):
            new_playlist = [path]
        elif os.path.exists(path):
            ext = ('.mp3', '.m4a', '.wav', '.flac', '.mp4', '.avi', '.mkv', '.webm')
            if os.path.isfile(path):
                directory = os.path.dirname(path)
                new_playlist.append(path)
                try:
                    others = [os.path.join(directory, f) for f in os.listdir(directory)
                             if f.lower().endswith(ext) and os.path.join(directory, f) != path]
                    if self.random_mode: random.shuffle(others)
                    new_playlist.extend(others)
                except: pass
            elif os.path.isdir(path):
                files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(ext)]
                if files:
                    if self.random_mode: random.shuffle(files)
                    new_playlist = files

        if new_playlist:
            self.playlist = new_playlist
            if self.is_playing:
                self.play_current()

    def toggle(self):
        if not self.is_playing:
            if self.playlist:
                self.is_playing = True
                self.play_current()
        else:
            if self.mw and hasattr(self.mw, 'player'):
                self.mw.player.toggle_pause()
            else:
                self.player.pause = not self.player.pause

    def play_current(self):
        if not self.playlist: return
        track = self.playlist[0]
        
        if self.mw and hasattr(self.mw, 'player'):
            # Chiamata sicura al player principale
            self.mw.player.load_media(track, is_radio=True, start_paused=False)
            self.player.command("stop")
        else:
            try:
                target_vol = 5 if self.is_ducked else self.base_volume
                self.player.volume = target_vol
                self.player.play(track)
                self.player.pause = False
            except: pass

    def set_ducking(self, enabled, force=False):
        self.is_ducked = enabled
        self.set_volume(self.base_volume)

    def next(self):
        if self.playlist:
            track = self.playlist.pop(0)
            self.playlist.append(track)
            self.play_current()

    def stop(self):
        self.player.command("stop")
        self.is_playing = False
