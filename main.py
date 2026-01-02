import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import yt_dlp
import os

# =====================
# WINDOW
# =====================
root = tk.Tk()
root.title("Video Downloader v2")
root.geometry("720x520")
root.configure(bg="#020617")
root.resizable(False, False)

# =====================
# STYLE
# =====================
BTN = {
    "font": ("Arial", 11),
    "bg": "#111827",
    "fg": "white",
    "activebackground": "#1e293b",
    "bd": 0,
    "padx": 12,
    "pady": 6
}

LABEL = {
    "bg": "#020617",
    "fg": "white",
    "font": ("Arial", 11)
}

# =====================
# STATE
# =====================
download_path = tk.StringVar()
is_downloading = False

# =====================
# UI
# =====================
tk.Label(root, text="URL Video", **LABEL).pack(anchor="w", padx=15, pady=(15, 0))
url_entry = tk.Entry(root, font=("Arial", 12))
url_entry.pack(fill="x", padx=15, pady=5)

tk.Label(root, text="Folder Tujuan", **LABEL).pack(anchor="w", padx=15)
path_frame = tk.Frame(root, bg="#020617")
path_frame.pack(fill="x", padx=15)

path_entry = tk.Entry(path_frame, textvariable=download_path, font=("Arial", 11))
path_entry.pack(side="left", fill="x", expand=True)

def browse():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)

tk.Button(path_frame, text="Browse", command=browse, **BTN).pack(side="left", padx=5)

tk.Label(root, text="Kualitas Download", **LABEL).pack(anchor="w", padx=15, pady=(15, 0))
quality_box = ttk.Combobox(
    root,
    values=[
        "Best (Video + Audio)",
        "720p",
        "480p",
        "Audio Only (MP3)"
    ],
    state="readonly"
)
quality_box.current(0)
quality_box.pack(fill="x", padx=15, pady=5)

progress_label = tk.Label(root, text="Progress: 0%", fg="#94a3b8", bg="#020617")
progress_label.pack(pady=(20, 5))

progress_bar = ttk.Progressbar(root, orient="horizontal", length=680, mode="determinate")
progress_bar.pack(pady=5)

status_label = tk.Label(root, text="Status: Idle", fg="#94a3b8", bg="#020617")
status_label.pack(pady=10)

# =====================
# DOWNLOAD LOGIC
# =====================
def start_download():
    global is_downloading
    if is_downloading:
        return

    url = url_entry.get().strip()
    folder = download_path.get()
    quality = quality_box.get()

    if not url or not folder:
        messagebox.showerror("Error", "URL dan folder wajib diisi")
        return

    is_downloading = True
    threading.Thread(
        target=download_video,
        args=(url, folder, quality),
        daemon=True
    ).start()

def download_video(url, folder, quality):
    global is_downloading

    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "")
            try:
                progress_label.config(text=f"Progress: {percent}%")
            except:
                pass
        elif d["status"] == "finished":
            progress_label.config(text="Progress: 100%")

    if quality == "720p":
        fmt = "bestvideo[height<=720]+bestaudio/best"
    elif quality == "480p":
        fmt = "bestvideo[height<=480]+bestaudio/best"
    elif quality == "Audio Only (MP3)":
        fmt = "bestaudio"
    else:
        fmt = "best"

    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "format": fmt,
        "progress_hooks": [hook],
        "quiet": True,
        "merge_output_format": "mp4"
    }

    if quality == "Audio Only (MP3)":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        status_label.config(text="Status: Downloading...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        status_label.config(text="Status: Selesai ✅")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Status: Error ❌")

    is_downloading = False

# =====================
# BUTTON
# =====================
tk.Button(root, text="DOWNLOAD", command=start_download, **BTN).pack(pady=15)

root.mainloop()
