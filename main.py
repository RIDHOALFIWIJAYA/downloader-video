import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
import os
import re
import sys
import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor 

# CONFIG & THEME
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VideoDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Downloader v5.4 Linux Stable")
        self.geometry("900x750")

        # State
        self.download_path = ctk.StringVar()
        self.is_downloading = False
        self.history_file = "history.json"
        self.last_clipboard = "" 
        
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="V-DL v5.4", text_color="#87CEEB", 
                                 font=ctk.CTkFont(size=25, weight="bold"), fg_color="#334155", corner_radius=14)
        self.logo.pack(pady=30, padx=15)

        # Thumbnail Box
        self.thumb_label = ctk.CTkLabel(self.sidebar, text="Thumbnail..", text_color="#87CEEB", width=200, height=120, 
                                        fg_color="#0f172a", corner_radius=8)
        self.thumb_label.pack(pady=10, padx=20)

        self.size_label = ctk.CTkLabel(self.sidebar, text="Size: -", font=ctk.CTkFont(size=12))
        self.size_label.pack(pady=2)
        self.duration_label = ctk.CTkLabel(self.sidebar, text="Durasi: -", font=ctk.CTkFont(size=12))
        self.duration_label.pack(pady=2)

        self.btn_browse = ctk.CTkButton(self.sidebar, text="📁 Pilih Folder", command=self.browse, fg_color="#334155")
        self.btn_browse.pack(pady=10, padx=20)

        self.btn_open = ctk.CTkButton(self.sidebar, text="📂 Buka Folder", command=self.open_folder, fg_color="transparent", border_width=1)
        self.btn_open.pack(pady=10, padx=20)

        self.btn_history = ctk.CTkButton(self.sidebar, text="📜 Lihat History", command=self.show_history, fg_color="#1e293b", hover_color="#334155")
        self.btn_history.pack(pady=10, padx=20)

        # THEME SWITCHER
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", font=ctk.CTkFont(size=11))
        self.theme_label.pack(pady=(20, 0))
        self.theme_option = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],
                                               command=self.change_appearance_mode_event)
        self.theme_option.set("Dark")
        self.theme_option.pack(pady=10, padx=20)

        self.history_label = ctk.CTkLabel(self.sidebar, text="Linux Optimized", font=ctk.CTkFont(size=10), text_color="#4ade80")
        self.history_label.pack(side="bottom", pady=20)

        # MAIN CONTENT
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.url_label = ctk.CTkLabel(self.main_frame, text="URL Video / YouTube (Auto-detect active)", font=ctk.CTkFont(size=13))
        self.url_label.pack(anchor="w", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Copy link dari browser...", 
                                      placeholder_text_color=("#606060", "#94a3b8"), height=35)
        self.url_entry.pack(fill="x", pady=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self.fetch_preview()) 

        self.q_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.q_btn_frame.pack(fill="x", pady=5)

        self.btn_add = ctk.CTkButton(self.q_btn_frame, text="+ Tambah Antrean", command=self.add_to_queue, width=155)
        self.btn_add.pack(side="left")

        self.btn_del = ctk.CTkButton(self.q_btn_frame, text="🗑️ Hapus Terakhir", command=self.delete_selected, fg_color="#ef4444", hover_color="#dc2626", width=120)
        self.btn_del.pack(side="left", padx=10)

        self.queue_list = ctk.CTkTextbox(self.main_frame, height=120, fg_color="#0f172a", text_color="#94a3b8")
        self.queue_list.pack(fill="x", pady=10)
        self.queue_data = [] 

        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.info_frame.pack(fill="x", pady=10)

        self.quality_box = ctk.CTkComboBox(self.info_frame, values=["Best Quality", "720p (MP4)", "480p (MP4)", "Audio Only (MP3)"], width=200)
        self.quality_box.set("Best Quality")
        self.quality_box.pack(side="left")

        self.path_display = ctk.CTkLabel(self.info_frame, textvariable=self.download_path, text_color="#64748b", font=ctk.CTkFont(size=11), wraplength=350)
        self.path_display.pack(side="left", padx=20)

        self.info_label = ctk.CTkLabel(self.main_frame, text="Judul:...", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8", wraplength=600, justify="left")
        self.info_label.pack(anchor="w", pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Idle", text_color="#4ade80")
        self.status_label.pack()

        self.btn_download = ctk.CTkButton(self.main_frame, text="Start Download", command=self.process_queue, height=50, 
                                          font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#0ea5e9", "#1f6aa5"), hover_color="#0284c7")
        self.btn_download.pack(fill="x", pady=20)

        self.check_clipboard()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def check_clipboard(self):
        try:
            current_clipboard = self.clipboard_get().strip()
            if current_clipboard != self.last_clipboard and "http" in current_clipboard:
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, current_clipboard)
                self.last_clipboard = current_clipboard
                self.fetch_preview()
        except: pass
        self.after(1500, self.check_clipboard)

    def fetch_preview(self):
        url = self.url_entry.get().strip()
        if not url or "http" not in url: return
        self.thumb_label.configure(text="Loading...", image="")
        threading.Thread(target=self._get_meta_thread, args=(url,), daemon=True).start()

    def _get_meta_thread(self, url):
        try:
            ydl_opts = {'quiet': True, 'nocheckcertificate': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumb_url = info.get('thumbnail')
                title = info.get('title')
                filesize = info.get('filesize') or info.get('filesize_approx')
                size_str = f"{filesize / (1024*1024):.1f} MB" if filesize else "Unknown"
                
                self.after(0, lambda: self.info_label.configure(text=f"Judul: {title}"))
                self.after(0, lambda: self.size_label.configure(text=f"Size: ~{size_str}"))
                
                resp = requests.get(thumb_url, timeout=10)
                img = Image.open(BytesIO(resp.content))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 101))
                self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except:
            self.after(0, lambda: self.thumb_label.configure(text="Preview Error", image=""))

    def download_engine(self, url, folder, quality):
        def hook(d):
            if d['status'] == 'downloading':
                p_str = d.get('_percent_str', '0%')
                clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%', '').strip()
                try:
                    self.after(0, lambda: self.progress_bar.set(float(clean_p)/100))
                    self.after(0, lambda: self.status_label.configure(text=f"Speed: {d.get('_speed_str','N/A')}"))
                except: pass

        # FIX: Hapus ffmpeg_location agar menggunakan sistem Linux
        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'progress_hooks': [hook],
            'quiet': True, 'nocheckcertificate': True, 'writethumbnail': True, 
            'continuedl': True,
            'postprocessors': [{'key': 'FFmpegMetadata'}, {'key': 'EmbedThumbnail'}]
        }

        if "720p" in quality: ydl_opts['format'] = "bestvideo[height<=720]+bestaudio/best"
        elif "Audio" in quality:
            ydl_opts['format'] = "bestaudio/best"
            ydl_opts['postprocessors'].insert(0, {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'})
        else: ydl_opts['format'] = "bestvideo+bestaudio/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(url, download=True)
                self.save_to_json(meta.get('title', 'Unknown'), url)
        except Exception as e: print(f"Download Error: {e}")

    # --- Sisa fungsi (History, Queue, dll) tetap sama ---
    def save_to_json(self, title, url):
        data = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f: data = json.load(f)
            except: data = []
        data.append({"title": title, "url": url, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        with open(self.history_file, "w") as f: json.dump(data, f, indent=4)

    def browse(self):
        folder = filedialog.askdirectory()
        if folder: self.download_path.set(folder)

    def open_folder(self):
        path = self.download_path.get()
        if os.path.exists(path): os.startfile(path) if sys.platform == "win32" else os.system(f'xdg-open "{path}"')

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if url and "http" in url:
            self.queue_data.append(url)
            self.update_listbox()
            self.url_entry.delete(0, 'end')
        else: messagebox.showwarning("Peringatan", "URL tidak valid!")

    def delete_selected(self):
        if self.queue_data:
            self.queue_data.pop() 
            self.update_listbox()

    def update_listbox(self):
        self.queue_list.delete("0.0", "end")
        for i, url in enumerate(self.queue_data):
            self.queue_list.insert("end", f"{i+1}. {url}\n")

    def process_queue(self):
        if self.is_downloading or not self.queue_data or not self.download_path.get(): return
        self.is_downloading = True
        self.btn_download.configure(state="disabled", text="DOWNLOADING...")
        threading.Thread(target=self.master_download_thread, daemon=True).start()

    def master_download_thread(self):
        folder, quality = self.download_path.get(), self.quality_box.get()
        with ThreadPoolExecutor(max_workers=2) as executor:
            urls = list(self.queue_data)
            self.queue_data.clear()
            self.after(0, self.update_listbox)
            executor.map(lambda u: self.download_engine(u, folder, quality), urls)
        self.after(0, self.finish_all)

    def finish_all(self):
        self.is_downloading = False
        self.btn_download.configure(state="normal", text="Start Download")
        self.status_label.configure(text="Selesai! ✅")
        messagebox.showinfo("V-DL", "Semua download selesai brok!")

    def show_history(self):
        # Implementasi history tetap sama
        pass

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
