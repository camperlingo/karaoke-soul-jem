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
        self._is_switching = False
        self._safe_to_sync = False 
        
        self.is_radio_mode = False
        self.viz_timer = 0
        self.current_viz_video = None

        # Parametri caricati in memoria, MA IL PLAYER NON VIENE CREATO QUI!
        self.params = {
            "vo": "gpu",
            "hwdec": "vaapi",
            "hwdec_codecs": "h264,vc1,wmv3,hevc", 
            "profile": "fast",                 
            "vd_lavc_fast": "yes",             
            "vd_lavc_skiploopfilter": "all",   
            "keep_open": "yes",
            "idle": "yes",
            "osc": False,
            "audio_pitch_correction": "yes",
            "audio_display": "no", 
            "video_sync": "audio", 
            "cache": "yes",
            "demuxer_max_bytes": "150M",
            "audio_buffer": "1.0",           
            "audio_stream_silence": "yes",
            "gpu_context": "x11egl",
            "vd_lavc_dr": "yes",
            "opengl_pbo": "yes",
            "input_default_bindings": "no",
            "input_vo_keyboard": "no",
            "reset_on_next_file": "all",
            "image_display_duration": "inf"
        }
        
        atexit.register(self.cleanup)

    def set_window(self, wid):
        """
        IL CUORE DELLA PATCH: Inizializziamo MPV *SOLO* quando 
        la finestra Tkinter esiste. Nessuna finestra "fuggiasca"!
        """
        try:
            self.main_wid = str(wid)
            
            # 1. Iniettiamo l'ID della GUI e forziamo lo schermo PRIMA di creare MPV
            self.params["wid"] = self.main_wid
            self.params["force_window"] = "immediate"
            
            self.player = mpv.MPV(**self.params)
            
            @self.player.event_callback('end-file')
            def on_end_file(event):
                if not self.sync_active or not getattr(self, 'mw', None) or self._is_loading or self._is_switching: 
                    return
                if hasattr(self.mw, 'bg_manager') and getattr(self.mw.bg_manager, 'is_playing', False):
                    self.mw.root.after(200, self.mw.bg_manager.next)

            # 2. Creiamo la SALA rimuovendo il 'wid' così si apre come seconda finestra
            sala_params = self.params.copy()
            del sala_params["wid"]
            sala_params["title"] = "SALA_KARAOKE"
            
            self.sala_player = mpv.MPV(**sala_params)
            
            try:
                self.sala_player.window_minimized = "yes"
            except: pass

            threading.Thread(target=self._continuous_sync, daemon=True).start()
            
            # Se c'è un logo o video salvato all'avvio, mostralo subito!
            if getattr(self, 'mw', None):
                bg = self.viz_manager.get_bg_file("", is_radio=True)
                if bg: self.mw.root.after(100, lambda: self.change_background(bg))
                
        except Exception as e:
            print(f"ERRORE CRITICO INIZIALIZZAZIONE MPV: {e}")


    def load_media(self, path, pitch=0, start_paused=True, is_radio=False):
        if not path or self._is_loading: return
        self._safe_to_sync = False 
        self.is_radio_mode = is_radio
        self.viz_timer = 0 
        
        if not is_radio:
            self._is_switching = True
            threading.Timer(3.0, self._reset_switching).start()

        self._is_loading = True 
        try:
            was_minimized = "yes"
            if hasattr(self, 'sala_player'):
                was_minimized = getattr(self.sala_player, 'window_minimized', "yes")
            
            bg_file = self.viz_manager.get_bg_file(path, is_radio)
            
            if hasattr(self, 'player'):
                self.player.command("loadfile", path, "replace")
            
            if hasattr(self, 'sala_player'):
                self.sala_player.command("loadfile", path, "replace")
                time.sleep(0.3)
                if was_minimized != "yes":
                    self.sala_player.window_minimized = "no"

            if bg_file and getattr(self, 'mw', None):
                self.mw.root.after(500, self.change_background, bg_file)

            if hasattr(self, 'player'):
                self.player.volume = 100 if not is_radio else self.mw.bg_manager.base_volume
                self.player.mute = False
                self.player.pause = start_paused
            
            if hasattr(self, 'sala_player'):
                self.sala_player.volume = 0
                self.sala_player.mute = True
                self.sala_player.pause = start_paused
            
            self.set_pitch(pitch)
        except Exception as e:
            print(f"[PLAYER] Errore caricamento: {e}")
        finally:
            self._is_loading = False 
            self._safe_to_sync = True 

    def change_background(self, bg_file):
        """Inietta a caldo o carica il logo a freddo con loop infinito"""
        if not bg_file: return
        self.current_viz_video = bg_file
        try:
            is_idle = True
            if hasattr(self, 'player'):
                is_idle = getattr(self.player, 'idle_active', True)
            
            if is_idle:
                # Se è in STOP, facciamo girare il video VJ in loop o fissiamo l'immagine
                if hasattr(self, 'player'):
                    self.player.command("loadfile", bg_file, "replace", "loop-file=inf")
                if hasattr(self, 'sala_player'):
                    self.sala_player.command("loadfile", bg_file, "replace", "loop-file=inf")
            else:
                # Se la musica SUONA, iniettiamo il video sopra la traccia audio
                if hasattr(self, 'player'):
                    self.player.command("video-add", bg_file, "select")
                    if getattr(self, 'mw', None): self.mw.root.after(300, lambda: self._cleanup_old_video_tracks(self.player))
                if hasattr(self, 'sala_player'):
                    self.sala_player.command("video-add", bg_file, "select")
                    if getattr(self, 'mw', None): self.mw.root.after(300, lambda: self._cleanup_old_video_tracks(self.sala_player))
        except Exception as e:
            print(f"[VIZ] Errore swap background: {e}")

    def _cleanup_old_video_tracks(self, player_instance):
        try:
            tracks = player_instance.track_list
            active_vid = None
            for t in tracks:
                if t.get('type') == 'video' and t.get('selected', False):
                    active_vid = t.get('id')
                    break
            for t in tracks:
                if t.get('type') == 'video' and t.get('external', False) and t.get('id') != active_vid:
                    player_instance.command("video-remove", t['id'])
        except: pass

    def _reset_switching(self):
        self._is_switching = False

    def stop(self):
        if self._is_loading: return
        self._safe_to_sync = False 
        try:
            if hasattr(self, 'player'): self.player.command("stop")
            if hasattr(self, 'sala_player'): self.sala_player.command("stop")
            if self._is_switching: return
            time.sleep(0.1) 
            if getattr(self, 'mw', None) and hasattr(self.mw, 'bg_manager') and getattr(self.mw.bg_manager, 'is_playing', False):
                self.mw.bg_manager.next()
                return
            if os.path.exists(self.black_file):
                self.load_media(self.black_file, start_paused=True)
                if hasattr(self, 'player'): self.player.volume = 0
        except: pass

    def toggle_sala(self):
        if not hasattr(self, 'sala_player'): return
        try:
            current = getattr(self.sala_player, 'window_minimized', "no")
            if current == "yes":
                self.sala_player.window_minimized = "no"
                if self._get_connected_monitors() > 1:
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
            if self._safe_to_sync:
                try:
                    if hasattr(self, 'player') and hasattr(self, 'sala_player'):
                        if not getattr(self.player, 'idle_active', True) and not getattr(self.player, 'pause', True):
                            p_pos = self.player.time_pos
                            s_pos = self.sala_player.time_pos
                            if p_pos is not None and s_pos is not None and abs(p_pos - s_pos) > 0.8:
                                self.sala_player.time_pos = p_pos
                except: pass
                
                # --- LOGICA TIMER: ROTAZIONE A 12 SECONDI ---
                try:
                    if getattr(self, 'is_radio_mode', False) and getattr(self.viz_manager, 'enabled', False) and getattr(self.viz_manager, 'video_folder', None):
                        if hasattr(self, 'player') and not getattr(self.player, 'pause', True):
                            self.viz_timer += 0.5
                            if self.viz_timer >= 12.0:
                                self.viz_timer = 0
                                new_vid = self.viz_manager.get_random_video(exclude=self.current_viz_video)
                                if new_vid and getattr(self, 'mw', None):
                                    self.mw.root.after(0, self.change_background, new_vid)
                except: pass

            time.sleep(0.5) 

    def toggle_pause(self, force_play=None):
        try:
            if not hasattr(self, 'player') or getattr(self.player, 'idle_active', True): return True
            st = not force_play if force_play is not None else not self.player.pause
            self.player.pause = st
            if hasattr(self, 'sala_player'): self.sala_player.pause = st
            return st
        except: return False

    def seek(self, percent):
        try:
            if hasattr(self, 'player'): self.player.percent_pos = float(percent)
            if hasattr(self, 'sala_player'): self.sala_player.percent_pos = float(percent)
        except: pass

    def set_pitch(self, val):
        try:
            speed = 2**(float(val)/12.0)
            if hasattr(self, 'player'): self.player.speed = speed
            if hasattr(self, 'sala_player'): self.sala_player.speed = speed
        except: pass

    def set_volume(self, val):
        try: 
            if hasattr(self, 'player'): self.player.volume = float(val)
        except: pass

    def _get_connected_monitors(self):
        try:
            out = subprocess.check_output("xrandr | grep ' connected' | wc -l", shell=True)
            return int(out.decode().strip())
        except: return 1

    def cleanup(self):
        self.sync_active = False 
        self._safe_to_sync = False
        time.sleep(0.1)          
        
        if hasattr(self, 'sala_player') and self.sala_player:
            try:
                self.sala_player.command("quit")
                self.sala_player.terminate() 
            except: pass
            
        if hasattr(self, 'player') and self.player:
            try:
                self.player.command("quit")
                self.player.terminate()      
            except: pass

Player = KaraokePlayer
