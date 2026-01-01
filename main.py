import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import yt_dlp
import os

# =====================
# WINDOW
# =====================
root = tk.Tk()
root.title("Social Media Video Downloader v1")
root.geometry("650x420")
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
    "padx": 10,
    "pady": 6
}

# =====================
# UI
# =====================
tk.Label(root, text="Video URL", fg="white", bg="#020617").pack(anchor="w", padx=10, pady=(10, 0))
url_entry = tk.Entry(root)
url_entry.pack(fill="x", padx=10, pady=5)

tk.Label(root, text="Folder Tujuan", fg="white", bg="#020617").pack(anchor="w", padx=10)
path_entry = tk.Entry(root)
path_entry.pack(fill="x", padx=10, pady=5)

def browse():
    folder = filedialog.askdirectory()
    if folder:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder)

tk.Button(root, text="Browse Folder", command=browse, **BTN).pack(pady=5)

progress_label = tk.Label(root, text="Progress: 0%", fg="white", bg="#020617")
progress_label.pack(pady=(10, 0))

progress_bar = ttk.Progressbar(root, orient="horizontal", length=580, mode="determinate")
progress_bar.pack(pady=5)

status_label = tk.Label(root, text="Status: Idle", fg="#94a3b8", bg="#020617")
status_label.pack(pady=5)

# =====================
# DOWNLOAD LOGIC
# =====================
def start_download():
    url = url_entry.get().strip()
    folder = path_entry.get().strip()

    if not url or not folder:
        messagebox.showerror("Error", "URL dan folder wajib diisi")
        return

    threading.Thread(
        target=download_video,
        args=(url, folder),
        daemon=True
    ).start()

def download_video(url, folder):
    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                progress_label.config(text=f"Progress: {percent}%")
            except:
                pass

        elif d["status"] == "finished":
            progress_label.config(text="Progress: 100%")

    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "format": "best",
        "progress_hooks": [hook],
        "quiet": True,
        "noplaylist": True
    }

    try:
        status_label.config(text="Status: Downloading...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        status_label.config(text="Status: Selesai ✅")
        messagebox.showinfo("Sukses", "Video berhasil didownload")

    except Exception as e:
        status_label.config(text="Status: Error ❌")
        messagebox.showerror("Error", str(e))

# =====================
# BUTTON
# =====================
tk.Button(root, text="Download Video", command=start_download, **BTN).pack(pady=15)

root.mainloop()

