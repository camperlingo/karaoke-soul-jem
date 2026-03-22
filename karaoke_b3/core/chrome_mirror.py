#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil

# ===============================
# CONFIGURAZIONE
# ===============================

PORT = 8000
PAGE = "mirror_client.html"

# ===============================
# RILEVA BROWSER
# ===============================

def find_browser():
    candidates = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser"
    ]

    for c in candidates:
        if shutil.which(c):
            return c

    return None


# ===============================
# AVVIO CHROME MIRROR
# ===============================

def launch_mirror(fullscreen=True):
    browser = find_browser()

    if not browser:
        print("❌ Chrome/Chromium non trovato.")
        sys.exit(1)

    url = f"http://localhost:{PORT}/{PAGE}"

    flags = [
        browser,
        "--no-first-run",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-translate",
        "--disable-notifications",
        "--disable-features=TranslateUI",
        "--disable-save-password-bubble",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-pinch",
        "--overscroll-history-navigation=0",
        f"--app={url}"
    ]

    if fullscreen:
        flags.append("--kiosk")

    print("🚀 Avvio MIRROR SALA")
    subprocess.Popen(flags)


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    launch_mirror(fullscreen=True)

