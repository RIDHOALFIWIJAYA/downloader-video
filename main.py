import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import yt_dlp
import os
import re
import sys

# =====================
# WINDOW & STYLE
# =====================
root = tk.Tk()
root.title("Video Downloader v3.0")
root.geometry("750x700")
root.configure(bg="#020617")
root.resizable(False, False)

BTN = {"font": ("Arial", 10, "bold"), "bg": "#1e293b", "fg": "white", "activebackground": "#334155", "bd": 0, "padx": 10, "pady": 5}
LABEL = {"bg": "#020617", "fg": "#f8fafc", "font": ("Arial", 10)}

download_path = tk.StringVar()
is_downloading = False
BASE_PATH = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

# =====================
# UI COMPONENTS
# =====================
# URL Input
tk.Label(root, text="URL Video / YouTube", **LABEL).pack(anchor="w", padx=25, pady=(20, 0))
url_entry = tk.Entry(root, font=("Arial", 11), bg="#1e293b", fg="white", insertbackground="white", bd=5, relief="flat")
url_entry.pack(fill="x", padx=25, pady=5)

# Queue & Folder Actions
action_frame = tk.Frame(root, bg="#020617")
action_frame.pack(fill="x", padx=25, pady=5)

def add_to_queue():
    url = url_entry.get().strip()
    if url:
        queue_listbox.insert(tk.END, url)
        url_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Peringatan", "Masukkan URL terlebih dahulu!")

tk.Button(action_frame, text="+ Tambah ke Antrean", command=add_to_queue, **BTN).pack(side="left")
tk.Button(action_frame, text="🗑️ Hapus Antrean", command=lambda: queue_listbox.delete(tk.ANCHOR), **BTN).pack(side="left", padx=10)

# Listbox for Queue
queue_listbox = tk.Listbox(root, height=5, bg="#0f172a", fg="#94a3b8", font=("Arial", 9), bd=0, highlightthickness=1)
queue_listbox.pack(fill="x", padx=25, pady=5)

# Folder Path
tk.Label(root, text="Folder Tujuan", **LABEL).pack(anchor="w", padx=25, pady=(10, 0))
path_frame = tk.Frame(root, bg="#020617")
path_frame.pack(fill="x", padx=25)

path_entry = tk.Entry(path_frame, textvariable=download_path, font=("Arial", 10), bg="#1e293b", fg="white", bd=5, relief="flat")
path_entry.pack(side="left", fill="x", expand=True)

def browse():
    folder = filedialog.askdirectory()
    if folder: download_path.set(folder)

tk.Button(path_frame, text="Browse", command=browse, **BTN).pack(side="left", padx=(10, 0))

# Quality Select
tk.Label(root, text="Kualitas & Format", **LABEL).pack(anchor="w", padx=25, pady=(15, 0))
quality_box = ttk.Combobox(root, values=["Best Quality", "720p (MP4)", "480p (MP4)", "Audio Only (MP3)"], state="readonly")
quality_box.current(0)
quality_box.pack(fill="x", padx=25, pady=5)

# Status & Progress
info_label = tk.Label(root, text="Judul: -", bg="#020617", font=("Arial", 10), fg="#38bdf8", wraplength=650, justify="left")
info_label.pack(anchor="w", padx=25, pady=10)

progress_label = tk.Label(root, text="Siap mengunduh", fg="#94a3b8", bg="#020617", font=("Arial", 9))
progress_label.pack(pady=(5, 0))

progress_bar = ttk.Progressbar(root, orient="horizontal", length=650, mode="determinate")
progress_bar.pack(pady=10, padx=25)

status_label = tk.Label(root, text="Status: Idle", fg="#4ade80", bg="#020617", font=("Arial", 10, "bold"))
status_label.pack(pady=5)

# =====================
# LOGIC
# =====================
def open_folder():
    path = download_path.get()
    if os.path.exists(path):
        os.startfile(path)

def process_queue():
    global is_downloading
    if is_downloading: return
    
    folder = download_path.get()
    if not folder:
        messagebox.showwarning("Peringatan", "Pilih folder tujuan dulu!")
        return

    urls = queue_listbox.get(0, tk.END)
    if not urls:
        messagebox.showwarning("Peringatan", "Antrean kosong!")
        return

    is_downloading = True
    btn_download.config(state="disabled", text="RUNNING...")
    
    threading.Thread(target=download_engine, args=(urls, folder), daemon=True).start()

def download_engine(urls, folder):
    global is_downloading
    quality = quality_box.get()

    def hook(d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%')
            clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%', '').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            size = d.get('_total_bytes_str', d.get('_total_bytes_estimate_str', 'N/A'))
            
            try:
                progress_bar['value'] = float(clean_p)
                progress_label.config(text=f"Size: {size} | Speed: {speed} | ETA: {eta}")
                root.update_idletasks()
            except: pass

    for url in urls:
        status_label.config(text=f"Status: Fetching info...", fg="#38bdf8")
        
        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'progress_hooks': [hook],
            'ffmpeg_location': BASE_PATH,
            'quiet': True,
            'nocheckcertificate': True
        }

        # Format Logic
        if quality == "720p (MP4)":
            ydl_opts['format'] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best"
        elif quality == "480p (MP4)":
            ydl_opts['format'] = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best"
        elif quality == "Audio Only (MP3)":
            ydl_opts['format'] = "bestaudio/best"
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
        else:
            ydl_opts['format'] = "bestvideo+bestaudio/best"
            ydl_opts['merge_output_format'] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Feature: Fetch Metadata
                meta = ydl.extract_info(url, download=False)
                info_label.config(text=f"Judul: {meta.get('title', 'Unknown')}")
                
                status_label.config(text=f"Status: Downloading...", fg="#fbbf24")
                ydl.download([url])
                
            # Hapus yang sudah selesai dari listbox
            queue_listbox.delete(0)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal download {url}\n{str(e)}")
            break

    status_label.config(text="Status: Semua Selesai! ✅", fg="#4ade80")
    is_downloading = False
    btn_download.config(state="normal", text="START DOWNLOAD QUEUE")
    messagebox.showinfo("Sukses", "Semua file dalam antrean telah diproses.")

# =====================
# ACTION BUTTONS
# =====================
btn_frame = tk.Frame(root, bg="#020617")
btn_frame.pack(pady=10)

BTN_BLUE = BTN.copy()
BTN_BLUE.update({"bg": "#0ea5e9"})

btn_download = tk.Button(btn_frame, text="START DOWNLOAD QUEUE", command=process_queue, **BTN_BLUE)
btn_download.pack(side="left", padx=5)
btn_download.pack(side="left", padx=5)

btn_folder = tk.Button(btn_frame, text="📂 Buka Folder", command=open_folder, **BTN)
btn_folder.pack(side="left", padx=5)

root.mainloop()
