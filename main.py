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

        self.title("Video Downloader v5.4") # Update Versi
        self.geometry("900(750") # Tinggi ditambah sedikit untuk menu tema

        # State
        self.download_path = ctk.StringVar()
        self.is_downloading = False
        self.history_file = "history.json"
        self.last_clipboard = "" 
        self.BASE_PATH = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="V-DL v5.4", text_color="#87CEEB", font=ctk.CTkFont(size=25, weight="bold"), fg_color="#334155", corner_radius=14)
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

        # --- NEW: THEME SWITCHER UI ---
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", font=ctk.CTkFont(size=11))
        self.theme_label.pack(pady=(20, 0))
        self.theme_option = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],
                                               command=self.change_appearance_mode_event)
        self.theme_option.set("Dark")
        self.theme_option.pack(pady=10, padx=20)
        # ------------------------------

        self.history_label = ctk.CTkLabel(self.sidebar, text="Tambahan Dark mode and Light mode", font=ctk.CTkFont(size=10), text_color="#4ade80")
        self.history_label.pack(side="bottom", pady=20)

        # MAIN CONTENT
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.url_label = ctk.CTkLabel(self.main_frame, text="URL Video / YouTube (Deteksi clipboard otomatis)", font=ctk.CTkFont(size=13))
        self.url_label.pack(anchor="w", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Copy link dari browser dan aplikasi akan mendeteksi...", height=35)
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

        self.btn_download = ctk.CTkButton(self.main_frame, text="Start Download", command=self.process_queue, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#0ea5e9", "#1f6aa5"), hover_color="#0284c7")
        self.btn_download.pack(fill="x", pady=20)

        self.check_clipboard()

    # --- NEW: THEME EVENT ---
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def check_clipboard(self):
        try:
            current_clipboard = self.clipboard_get().strip()
            if current_clipboard != self.last_clipboard:
                if "http" in current_clipboard:
                    self.url_entry.delete(0, 'end')
                    self.url_entry.insert(0, current_clipboard)
                    self.last_clipboard = current_clipboard
                    self.fetch_preview()
        except: pass
        self.after(1500, self.check_clipboard)

    def show_history(self):
        history_window = ctk.CTkToplevel(self)
        history_window.title("History Download")
        history_window.geometry("700x550")
        history_window.attributes('-topmost', True)
        ctk.CTkLabel(history_window, text="Riwayat Download Video", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        scroll_frame = ctk.CTkScrollableFrame(history_window, width=650, height=380)
        scroll_frame.pack(padx=20, pady=5, fill="both", expand=True)
        btn_clear = ctk.CTkButton(history_window, text="🗑️ Bersihkan Semua History", fg_color="#ef4444", hover_color="#dc2626", command=lambda: self.clear_history(history_window))
        btn_clear.pack(pady=15)

        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    if not data:
                        ctk.CTkLabel(scroll_frame, text="History masih kosong brok.").pack(pady=20)
                    for item in reversed(data):
                        card = ctk.CTkFrame(scroll_frame, fg_color="#1e293b", corner_radius=8)
                        card.pack(fill="x", pady=5, padx=5)
                        title_lbl = ctk.CTkLabel(card, text=f"🎥 {item['title']}", anchor="w", font=ctk.CTkFont(weight="bold"), wraplength=600, justify="left")
                        title_lbl.pack(padx=10, pady=(8,0), anchor="w")
                        info_lbl = ctk.CTkLabel(card, text=f"📅 {item['timestamp']} | 🔗 {item['url'][:50]}...", font=ctk.CTkFont(size=10), text_color="#94a3b8")
                        info_lbl.pack(padx=10, pady=(0,8), anchor="w")
            except: ctk.CTkLabel(scroll_frame, text="Gagal baca file history.").pack()
        else: ctk.CTkLabel(scroll_frame, text="Belum ada riwayat download.").pack()

    def clear_history(self, window):
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat download?"):
            with open(self.history_file, "w") as f: json.dump([], f)
            window.destroy()
            messagebox.showinfo("Sukses", "History berhasil dibersihkan!")

    def fetch_preview(self):
        url = self.url_entry.get().strip()
        if not url: return
        self.thumb_label.configure(text="Loading...", image=None)
        self.size_label.configure(text="Size: Fetching...")
        threading.Thread(target=self._get_meta_thread, args=(url,), daemon=True).start()

    def _get_meta_thread(self, url):
        try:
            ydl_opts = {'quiet': True, 'nocheckcertificate': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumb_url = info.get('thumbnail')
                title = info.get('title')
                filesize = info.get('filesize') or info.get('filesize_approx')
                size_str = f"{filesize / (1024*1024):.1f} MB" if filesize else "Unknown"
                duration = info.get('duration')
                dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "-:--"
                self.after(0, lambda: self.info_label.configure(text=f"Judul: {title}"))
                self.after(0, lambda: self.size_label.configure(text=f"Size: ~{size_str}"))
                self.after(0, lambda: self.duration_label.configure(text=f"Durasi: {dur_str}"))
                response = requests.get(thumb_url, verify=False, timeout=10)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 101))
                self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except: self.after(0, lambda: self.thumb_label.configure(text="Thumbnail Error", image=None))

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
        if os.path.exists(path): os.startfile(path)

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if url:
            self.queue_data.append(url)
            self.update_listbox()
            self.url_entry.delete(0, 'end')
            self.last_clipboard = "" 
        else: messagebox.showwarning("Peringatan", "Isi URL dulu brok!")

    def delete_selected(self):
        if self.queue_data:
            self.queue_data.pop() 
            self.update_listbox()

    def update_listbox(self):
        self.queue_list.delete("0.0", "end")
        for i, url in enumerate(self.queue_data):
            self.queue_list.insert("end", f"{i+1}. {url}\n")

    def process_queue(self):
        if self.is_downloading: return
        if not self.download_path.get() or not self.queue_data:
            messagebox.showwarning("Peringatan", "Lengkapi folder & antrean!")
            return
        self.is_downloading = True
        self.btn_download.configure(state="disabled", text="TURBO DOWNLOADING...")
        threading.Thread(target=self.master_download_thread, daemon=True).start()

    def master_download_thread(self):
        folder = self.download_path.get()
        quality = self.quality_box.get()
        with ThreadPoolExecutor(max_workers=3) as executor:
            urls = list(self.queue_data)
            self.queue_data.clear()
            self.after(0, self.update_listbox)
            executor.map(lambda u: self.download_engine(u, folder, quality), urls)
        self.after(0, self.finish_all)

    def download_engine(self, url, folder, quality):
        def hook(d):
            if d['status'] == 'downloading':
                p_str = d.get('_percent_str', '0%')
                clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%', '').strip()
                try:
                    val = float(clean_p) / 100
                    self.after(0, lambda: self.progress_bar.set(val))
                    speed = d.get('_speed_str', 'N/A')
                    self.after(0, lambda: self.status_label.configure(text=f"Turbo Speed: {speed}"))
                except: pass

        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'progress_hooks': [hook],
            'ffmpeg_location': self.BASE_PATH,
            'quiet': True, 'nocheckcertificate': True, 'writethumbnail': True, 
            'retries': 15, 'fragment_retries': 15, 'retry_sleep': 5, 'continuedl': True,
            'postprocessors': [{'key': 'FFmpegMetadata', 'add_metadata': True}, {'key': 'EmbedThumbnail'}]
        }

        if "720p" in quality: ydl_opts['format'] = "bestvideo[height<=720][vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"
        elif "480p" in quality: ydl_opts['format'] = "bestvideo[height<=480][vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"
        elif "Audio" in quality:
            ydl_opts['format'] = "bestaudio/best"
            ydl_opts['postprocessors'].insert(0, {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'})
        else: ydl_opts['format'] = "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"

        if "Audio" not in quality: ydl_opts['merge_output_format'] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(url, download=True)
                self.save_to_json(meta.get('title', 'Unknown'), url)
        except Exception as e:
            print(f"Thread Error: {e}")

    def finish_all(self):
        self.status_label.configure(text="Semua Antrean Selesai! ✅", text_color="#4ade80")
        self.is_downloading = False
        self.btn_download.configure(state="normal", text="Start Download")
        self.progress_bar.set(0)
        if os.path.exists(self.download_path.get()):
            os.startfile(self.download_path.get())

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
