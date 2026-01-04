import mpv
import os
import atexit
import subprocess
import threading
import time
from .visualizer_logic import Visualizer 

class KaraokePlayer:
    def __init__(self, main_window=None):
        self.mw = main_window 
        self.black_file = os.path.expanduser("~/karaoke_clean/assets/black.mp4")
        self.main_wid = None
        self.sync_active = True
        self.viz_manager = Visualizer()
        self._is_loading = False 
        self._is_switching = False # SCUDO INTERNO AUTOMATICO

        self.params = {
            "vo": "gpu",
            "hwdec": "vaapi",                
            "hwdec-codecs": "h264,vc1,wmv3,hevc", 
            "keep_open": "yes",
            "idle": "yes",
            "osc": False,
            "audio_pitch_correction": "yes",
            "audio-display": "no", 
            "video_sync": "audio", 
            "cache": "yes",
            "demuxer-max-bytes": "200M",
            "demuxer-max-back-bytes": "50M",
            "audio-buffer": "1.0",           
            "audio-stream-silence": "yes",
            "gpu-context": "x11egl",
            "vd-lavc-dr": "yes",
            "opengl-pbo": "yes",
            "input_default_bindings": "no",
            "input_vo_keyboard": "no",
            "reset_on_next_file": "all",
        }
        
        try:
            self.player = mpv.MPV(**self.params, force_window="no")
            
            @self.player.event_callback('end-file')
            def on_end_file(event):
                # Se stiamo cambiando brano o caricando, ignoriamo l'evento fine-file
                if not self.sync_active or not self.mw or self._is_loading or self._is_switching: 
                    return
                
                if hasattr(self.mw, 'bg_manager'):
                    if self.mw.bg_manager.is_playing:
                        print("[SISTEMA] Fine brano, rotazione radio...")
                        self.mw.root.after(200, self.mw.bg_manager.next)

            self.sala_player = mpv.MPV(**self.params, title="SALA_KARAOKE", volume=0, force_window="yes")
            
            try:
                self.sala_player.window_minimized = "yes"
            except: pass

            threading.Thread(target=self._continuous_sync, daemon=True).start()
        except Exception as e:
            print(f"ERRORE CRITICO: {e}")

        atexit.register(self.cleanup)

    def load_media(self, path, pitch=0, start_paused=True, is_radio=False):
        if not path or self._is_loading: return
        
        # Se carichiamo una base (non radio), attiviamo lo scudo protettivo
        if not is_radio:
            self._is_switching = True
            # Rimuoviamo lo scudo dopo 3 secondi
            threading.Timer(3.0, self._reset_switching).start()

        self._is_loading = True 
        opts = self.viz_manager.get_options(path, is_radio=is_radio)
        
        try:
            was_minimized = self.sala_player.window_minimized == "yes"
            self.player.command("loadfile", path, "replace", opts)
            self.sala_player.command("loadfile", path, "replace", opts)
            
            time.sleep(0.3)
            if not was_minimized:
                self.sala_player.window_minimized = "no"

            if is_radio and self.mw and hasattr(self.mw, 'bg_manager'):
                self.player.volume = self.mw.bg_manager.base_volume
            else:
                self.player.volume = 100
                
            self.player.mute = False
            self.sala_player.volume = 0
            self.sala_player.mute = True
            self.player.pause = start_paused
            self.sala_player.pause = start_paused
            self.set_pitch(pitch)
        except Exception as e:
            print(f"[PLAYER] Errore: {e}")
        finally:
            self._is_loading = False 

    def _reset_switching(self):
        self._is_switching = False

    def stop(self):
        """Ferma tutto. Se stiamo cambiando brano, impedisce alla radio di rubare il focus."""
        if self._is_loading: return
        try:
            self.player.command("stop")
            self.sala_player.command("stop")
            
            # Se lo scudo è attivo, NON far ripartire la radio
            if self._is_switching:
                return

            if self.mw and hasattr(self.mw, 'bg_manager'):
                if self.mw.bg_manager.is_playing:
                    self.mw.bg_manager.next()
                    return

            if os.path.exists(self.black_file):
                self.load_media(self.black_file, start_paused=True)
                self.player.volume = 0
        except: pass

    # ... (metodi toggle_sala, _continuous_sync, set_window, ecc. rimangono uguali)
    def toggle_sala(self):
        try:
            current = self.sala_player.window_minimized
            if current == "yes":
                self.sala_player.window_minimized = "no"
                num = self._get_connected_monitors()
                if num > 1:
                    self.sala_player.fullscreen = "yes"
                    self.sala_player.geometry = "+1920+0"
                else:
                    self.sala_player.fullscreen = "no"
                    self.sala_player.geometry = "480x270+50+50"
                    self.sala_player.ontop = "yes"
            else:
                self.sala_player.window_minimized = "yes"
        except: pass

    def _continuous_sync(self):
        while self.sync_active:
            try:
                if not self.player.pause and self.player.time_pos is not None:
                    p_pos = self.player.time_pos
                    s_pos = self.sala_player.time_pos
                    if s_pos is not None and abs(p_pos - s_pos) > 0.3:
                        self.sala_player.time_pos = p_pos
            except: pass
            time.sleep(1.0) 

    def set_window(self, wid):
        try:
            self.main_wid = str(wid)
            self.player.wid = self.main_wid
        except: pass

    def toggle_pause(self, force_play=None):
        try:
            if self.player.idle_active: return True
            new_state = not force_play if force_play is not None else not self.player.pause
            self.player.pause = new_state
            self.sala_player.pause = new_state
            return new_state
        except: return False

    def seek(self, percent):
        try:
            self.player.percent_pos = float(percent)
            self.sala_player.percent_pos = float(percent)
        except: pass

    def set_pitch(self, val):
        try:
            speed = 2**(float(val)/12.0)
            self.player.speed = speed
            self.sala_player.speed = speed
        except: pass

    def set_volume(self, val):
        try: self.player.volume = float(val)
        except: pass

    def _get_connected_monitors(self):
        try:
            cmd = "xrandr | grep ' connected' | wc -l"
            out = subprocess.check_output(cmd, shell=True)
            return int(out.decode().strip())
        except: return 1

    def cleanup(self):
        self.sync_active = False
        try:
            self.player.terminate()
            self.sala_player.terminate()
        except: pass

Player = KaraokePlayer
