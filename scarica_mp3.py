import yt_dlp
import os

# Cartella dove salvare i file
SAVE_PATH = os.path.expanduser("~/karaoke_clean/MP3_DOWNLOADS")

def download_audio():
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
        print(f"📁 Creata cartella: {SAVE_PATH}")

    print(f"\n--- SCARICATORE MP3 RAPIDO ---")
    print(f"I file verranno salvati in: {SAVE_PATH}")
    print("Scrivi 'esci' per chiudere.\n")

    while True:
        url = input("Incolla URL YouTube: ").strip()
        
        if url.lower() in ('esci', 'exit', 'q'):
            print("Ciao!")
            break
        
        if not url:
            continue

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(SAVE_PATH, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("⬇️  Avvio download e conversione...")
                ydl.download([url])
                print("✅ Fatto! Pronto per il prossimo.")
        except Exception as e:
            print(f"❌ Errore: {e}")

if __name__ == "__main__":
    download_audio()
