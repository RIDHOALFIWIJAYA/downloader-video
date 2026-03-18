import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
import os
import re
import sys

# =====================
# CONFIG & THEME
# =====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VideoDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Downloader v3.5")
        self.geometry("850x600")
        
        # State
        self.download_path = ctk.StringVar()
        self.is_downloading = False
        self.BASE_PATH = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =====================
        # SIDEBAR
        # =====================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="V-DL PRO", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.pack(pady=30, padx=20)

        self.btn_browse = ctk.CTkButton(self.sidebar, text="📁 Pilih Folder", command=self.browse, fg_color="#334155")
        self.btn_browse.pack(pady=10, padx=20)
        
        self.btn_open = ctk.CTkButton(self.sidebar, text="📂 Buka Folder", command=self.open_folder, fg_color="transparent", border_width=1)
        self.btn_open.pack(pady=10, padx=20)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Theme: Dark", anchor="w")
        self.appearance_mode_label.pack(side="bottom", padx=20, pady=(0, 20))
        
        # =====================
        # MAIN CONTENT
        # =====================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # URL Input Section
        self.url_label = ctk.CTkLabel(self.main_frame, text="URL Video / YouTube", font=ctk.CTkFont(size=13))
        self.url_label.pack(anchor="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Paste link di sini...", height=40)
        self.url_entry.pack(fill="x", pady=(0, 10))

        # Queue Buttons
        self.q_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.q_btn_frame.pack(fill="x", pady=5)
        
        self.btn_add = ctk.CTkButton(self.q_btn_frame, text="+ Tambah Antrean", command=self.add_to_queue, width=150)
        self.btn_add.pack(side="left")
        
        self.btn_del = ctk.CTkButton(self.q_btn_frame, text="🗑️ Hapus", command=self.delete_selected, fg_color="#ef4444", hover_color="#dc2626", width=100)
        self.btn_del.pack(side="left", padx=10)

        # Queue List
        self.queue_list = ctk.CTkTextbox(self.main_frame, height=120, fg_color="#0f172a", text_color="#94a3b8")
        self.queue_list.pack(fill="x", pady=10)
        self.queue_data = [] 

        # Quality & Folder Info
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.info_frame.pack(fill="x", pady=10)

        self.quality_box = ctk.CTkComboBox(self.info_frame, values=["Best Quality", "720p (MP4)", "480p (MP4)", "Audio Only (MP3)"], width=200)
        self.quality_box.set("Best Quality")
        self.quality_box.pack(side="left")
        
        self.path_display = ctk.CTkLabel(self.info_frame, textvariable=self.download_path, text_color="#64748b", font=ctk.CTkFont(size=11))
        self.path_display.pack(side="left", padx=20)

        # Progress Section
        self.info_label = ctk.CTkLabel(self.main_frame, text="Judul: -", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8")
        self.info_label.pack(anchor="w", pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Idle", text_color="#4ade80")
        self.status_label.pack()

        self.btn_download = ctk.CTkButton(self.main_frame, text="DOWNLOAD SEKARANG", command=self.process_queue, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#0ea5e9", hover_color="#0284c7")
        self.btn_download.pack(fill="x", pady=20)

    # =====================
    # LOGIC FUNCTIONS
    # =====================
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
        else:
            messagebox.showwarning("Peringatan", "Isi URL dulu brok!")

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
        if not self.download_path.get():
            messagebox.showwarning("Peringatan", "Pilih folder dulu!")
            return
        if not self.queue_data:
            messagebox.showwarning("Peringatan", "Antrean kosong!")
            return

        self.is_downloading = True
        self.btn_download.configure(state="disabled", text="SEDANG PROSES...")
        threading.Thread(target=self.download_engine, daemon=True).start()

    def download_engine(self):
        folder = self.download_path.get()
        quality = self.quality_box.get()

        def hook(d):
            if d['status'] == 'downloading':
                p_str = d.get('_percent_str', '0%')
                clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%', '').strip()
                try:
                    val = float(clean_p) / 100
                    self.progress_bar.set(val)
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    self.status_label.configure(text=f"Speed: {speed} | ETA: {eta}")
                except:
                    pass

        while self.queue_data:
            url = self.queue_data[0]
            self.status_label.configure(text="Status: Fetching Metadata...", text_color="#38bdf8")
            
            ydl_opts = {
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'ffmpeg_location': self.BASE_PATH,
                'quiet': True,
                'nocheckcertificate': True
            }

            # Format Logic: Memaksa H.264 (avc1)
            if "720p" in quality:
                ydl_opts['format'] = "bestvideo[height<=720][vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"
                ydl_opts['merge_output_format'] = "mp4"
            elif "480p" in quality:
                ydl_opts['format'] = "bestvideo[height<=480][vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"
                ydl_opts['merge_output_format'] = "mp4"
            elif "Audio" in quality:
                ydl_opts['format'] = "bestaudio/best"
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            else:
                ydl_opts['format'] = "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best"
                ydl_opts['merge_output_format'] = "mp4"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    meta = ydl.extract_info(url, download=False)
                    title = meta.get('title', 'Unknown')
                    self.info_label.configure(text=f"Judul: {title[:70]}...")
                    
                    self.status_label.configure(text="Status: Downloading...", text_color="#fbbf24")
                    ydl.download([url])
                
                # Selesai satu, hapus dari list
                self.queue_data.pop(0)
                self.after(0, self.update_listbox)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Gagal download {url}\n{str(e)}"))
                break 

        self.status_label.configure(text="Semua Selesai! ✅", text_color="#4ade80")
        self.is_downloading = False
        self.btn_download.configure(state="normal", text="DOWNLOAD SEKARANG")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
