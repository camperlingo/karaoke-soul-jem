#!/usr/bin/env python3
import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Configurazione base
DEFAULT_DIR = os.path.expanduser("~/karaoke_clean/MP3_DOWNLOADS")

# ================= LOGICA =================

def pulisci_cache_manuale():
    try:
        with yt_dlp.YoutubeDL() as ydl:
            ydl.cache.remove()
        messagebox.showinfo("Cache Pulita", "Memoria temporanea pulita!\nRiprova a scaricare.")
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile pulire la cache: {e}")

def ottieni_titolo():
    url = url_entry.get().strip()
    
    # 1. CONTROLLO LINK VALIDO (Nuovo)
    if not url:
        messagebox.showwarning("Attenzione", "Incolla prima un link!")
        return
    if not url.lower().startswith("http"):
        messagebox.showerror("Link Errato", "Quello che hai scritto non è un indirizzo web.\nDevi incollare un link completo (es: https://www.youtube.com...)")
        return

    btn_cerca.config(state="disabled")
    status_label.config(text="⏳ Analisi del link...", fg="blue")
    
    def worker():
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                titolo = info.get('title', 'Video senza titolo')
                # Pulizia caratteri
                titolo = "".join([c for c in titolo if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                root.after(0, lambda t=titolo: _imposta_titolo(t))
        except Exception as e:
            # FIX CRASH: Salviamo l'errore in una variabile stringa PRIMA di passarlo
            msg_errore = str(e)
            root.after(0, lambda m=msg_errore: _gestisci_errore_titolo(m))
        finally:
            root.after(0, lambda: btn_cerca.config(state="normal"))

    threading.Thread(target=worker, daemon=True).start()

def _imposta_titolo(titolo):
    name_entry.delete(0, tk.END)
    name_entry.insert(0, titolo)
    status_label.config(text="✅ Titolo trovato. Premi SCARICA.", fg="green")
    btn_scarica.config(state="normal", bg="#4CAF50")

def _gestisci_errore_titolo(msg):
    # Se fallisce (es. non è un link valido o errore 403), non crasha più
    status_label.config(text="⚠️ Scrivi il nome manualmente!", fg="orange")
    messagebox.showwarning("Titolo non trovato", 
                           f"Non riesco a leggere il titolo automaticamente.\nErrore: {msg}\n\n"
                           "Nessun problema: SCRIVI TU IL NOME del file e premi Scarica.")
    btn_scarica.config(state="normal", bg="#4CAF50")

def scarica():
    url = url_entry.get().strip()
    nome_file = name_entry.get().strip()
    folder = folder_var.get()
    
    if not url: return
    if not nome_file:
        messagebox.showwarning("Nome Mancante", "Inserisci un nome per il file!")
        return

    # Blocca interfaccia
    btn_scarica.config(state="disabled")
    btn_cerca.config(state="disabled")
    name_entry.config(state="disabled")
    
    # Reset Grafico
    progress["value"] = 0
    status_label.config(text="🚀 Avvio...", fg="blue")
    percent_label.config(text="0%")

    def worker():
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(folder, f"{nome_file}.%(ext)s"),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [lambda d: update_bar(d)],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            root.after(0, lambda: finish_success())

        except Exception as e:
            # FIX CRASH ANCHE QUI
            msg_errore = str(e)
            root.after(0, lambda m=msg_errore: finish_error(m))

    threading.Thread(target=worker, daemon=True).start()

# ================= AGGIORNAMENTO STATO AVANZATO =================
def update_bar(d):
    if d['status'] == 'downloading':
        try:
            # Calcola percentuale
            p = d.get('_percent_str', '0%').replace('%','')
            val = float(p)
            
            # Aggiorna GUI
            root.after(0, lambda: progress.config(value=val))
            root.after(0, lambda: percent_label.config(text=f"{val}%"))
            root.after(0, lambda: status_label.config(text="⬇️ Scaricamento dati...", fg="orange"))
        except: pass
        
    elif d['status'] == 'finished':
        # QUANDO IL DOWNLOAD FINISCE, PARTE LA CONVERSIONE
        root.after(0, lambda: progress.config(value=100))
        root.after(0, lambda: percent_label.config(text="100%"))
        root.after(0, lambda: status_label.config(text="⚙️ CONVERSIONE MP3 IN CORSO...\n(Non chiudere, ci mette qualche secondo!)", fg="red", font=("Arial", 10, "bold")))

def finish_success():
    status_label.config(text="✅ TUTTO FATTO! File Salvato.", fg="green", font=("Arial", 10, "bold"))
    percent_label.config(text="COMPLETATO")
    messagebox.showinfo("Successo", "Download e Conversione completati!")
    
    # Reset
    btn_scarica.config(state="normal")
    btn_cerca.config(state="normal")
    name_entry.config(state="normal")
    url_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    progress["value"] = 0
    percent_label.config(text="")

def finish_error(msg):
    status_label.config(text="❌ Errore", fg="red")
    messagebox.showerror("Errore", f"Si è verificato un errore:\n{msg}")
    
    btn_scarica.config(state="normal")
    btn_cerca.config(state="normal")
    name_entry.config(state="normal")

def scegli_cartella():
    d = filedialog.askdirectory()
    if d: folder_var.set(d)

# ================= GUI INTERFACE (V5.1 BUGFIX) =================
root = tk.Tk()
root.title("Karaoke Downloader (V5.1 Stable)")
root.geometry("600x520")
root.resizable(False, False)

# Stili
style = ttk.Style()
style.theme_use('clam')
style.configure("green.Horizontal.TProgressbar", foreground='#4CAF50', background='#4CAF50')

main_frame = tk.Frame(root, padx=25, pady=25)
main_frame.pack(fill="both", expand=True)

# 0. Cache Cleaner
tk.Button(main_frame, text="🧹 Pulisci Cache", command=pulisci_cache_manuale, bg="#FFEBEE", fg="red", font=("Arial", 8)).pack(anchor="ne")

# 1. Cartella
frame_top = tk.Frame(main_frame)
frame_top.pack(fill="x", pady=(0, 10))
folder_var = tk.StringVar(value=DEFAULT_DIR)
tk.Label(frame_top, text="Salva in:", font=("Arial", 10, "bold")).pack(anchor="w")
f_box = tk.Frame(frame_top)
f_box.pack(fill="x")
tk.Entry(f_box, textvariable=folder_var, bg="#f0f0f0").pack(side="left", fill="x", expand=True, ipady=5)
tk.Button(f_box, text="📂", command=scegli_cartella).pack(side="left", padx=5)

# 2. URL e Ricerca
frame_url = tk.Frame(main_frame)
frame_url.pack(fill="x", pady=10)
tk.Label(frame_url, text="Link YouTube (es: https://youtu.be/...):", font=("Arial", 10, "bold")).pack(anchor="w")

url_box = tk.Frame(frame_url)
url_box.pack(fill="x")

url_entry = tk.Entry(url_box, font=("Arial", 11))
url_entry.pack(side="left", fill="x", expand=True, ipady=5)
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Incolla", command=lambda: url_entry.event_generate("<<Paste>>"))
url_entry.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

btn_cerca = tk.Button(url_box, text="🔍 Cerca", command=ottieni_titolo, bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
btn_cerca.pack(side="left", padx=5)

# 3. Nome File
frame_name = tk.Frame(main_frame)
frame_name.pack(fill="x", pady=10)
tk.Label(frame_name, text="Nome File:", font=("Arial", 10, "bold")).pack(anchor="w")
name_entry = tk.Entry(frame_name, font=("Arial", 11), fg="#333")
name_entry.pack(fill="x", ipady=5)

# 4. Download
frame_bot = tk.Frame(main_frame, pady=10)
frame_bot.pack(fill="x")

btn_scarica = tk.Button(frame_bot, text="⬇ SCARICA MP3", bg="#cccccc", fg="black", font=("Arial", 12, "bold"), command=scarica, state="disabled", height=2)
btn_scarica.pack(fill="x")

# 5. AREA PROGRESSO
progress_frame = tk.Frame(main_frame, pady=10)
progress_frame.pack(fill="x")

# Etichetta Percentuale GRANDE
percent_label = tk.Label(progress_frame, text="0%", font=("Arial", 20, "bold"), fg="#4CAF50")
percent_label.pack()

progress = ttk.Progressbar(progress_frame, length=500, mode='determinate', style="green.Horizontal.TProgressbar")
progress.pack(fill="x", pady=5)

# Etichetta Stato (Cosa sta facendo)
status_label = tk.Label(progress_frame, text="Pronto.", font=("Arial", 10), fg="#555")
status_label.pack()

os.makedirs(DEFAULT_DIR, exist_ok=True)
root.mainloop()
