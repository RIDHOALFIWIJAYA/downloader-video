import os
import sys

import customtkinter as ctk

CLIPBOARD_POLL_MS = 1500
MAX_HISTORY_DISPLAY = 20
MAX_DOWNLOAD_WORKERS = 2
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
HISTORY_FILE = "history.json"
APP_TITLE = "V-Downloader"
WINDOW_SIZE = "900x750"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")
