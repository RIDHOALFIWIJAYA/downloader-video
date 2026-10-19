import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox, TclError
from urllib.parse import urlparse

import customtkinter as ctk
import requests
import yt_dlp

from .config import (
    APP_TITLE,
    CLIPBOARD_POLL_MS,
    DEFAULT_DOWNLOAD_DIR,
    MAX_DOWNLOAD_WORKERS,
    WINDOW_SIZE,
)
from .downloader import download_video
from .history import append_history, clear_history, load_history
from .preview import fetch_video_info
from .ui import build_history_window, build_main_panel, build_sidebar


class VideoDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)

        self.download_path = ctk.StringVar(value=DEFAULT_DOWNLOAD_DIR)
        self.is_downloading = False
        self.cancel_download = False
        self.last_clipboard = ""
        self.queue_lock = threading.Lock()
        self.queue_data = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()
        self.check_clipboard()

    def _build_ui(self):
        if sys.platform == "win32":
            platform_text = "Windows"
        elif sys.platform == "darwin":
            platform_text = "macOS"
        else:
            platform_text = "Linux"

        sidebar = build_sidebar(
            self,
            download_path_var=self.download_path,
            platform_text=platform_text,
            on_browse=self.browse,
            on_open_folder=self.open_folder,
            on_history=self.show_history,
            on_theme=self.change_appearance_mode_event,
        )
        main_panel = build_main_panel(
            self,
            download_path_var=self.download_path,
            on_fetch=self.fetch_preview,
            on_add=self.add_to_queue,
            on_remove=self.delete_selected,
            on_download=self.process_queue,
            on_cancel=self.cancel_active_download,
        )

        self.thumb_label = sidebar.thumb_label
        self.size_label = sidebar.size_label
        self.duration_label = sidebar.duration_label

        self.url_entry = main_panel.url_entry
        self.queue_list = main_panel.queue_list
        self.quality_box = main_panel.quality_box
        self.info_label = main_panel.info_label
        self.progress_bar = main_panel.progress_bar
        self.status_label = main_panel.status_label
        self.btn_download = main_panel.btn_download
        self.btn_cancel = main_panel.btn_cancel

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def _is_valid_url(self, url):
        try:
            result = urlparse(url)
            return result.scheme in ("http", "https") and bool(result.netloc)
        except (ValueError, TypeError):
            return False

    def check_clipboard(self):
        try:
            current_clipboard = self.clipboard_get().strip()
            if current_clipboard != self.last_clipboard and self._is_valid_url(current_clipboard):
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, current_clipboard)
                self.last_clipboard = current_clipboard
                self.fetch_preview()
        except (TclError, OSError):
            pass
        self.after(CLIPBOARD_POLL_MS, self.check_clipboard)

    def fetch_preview(self):
        url = self.url_entry.get().strip()
        if not url or not self._is_valid_url(url):
            return
        self.thumb_label.configure(text="Loading...", image="")
        threading.Thread(target=self._get_meta_thread, args=(url,), daemon=True).start()

    def _get_meta_thread(self, url):
        try:
            info = fetch_video_info(url)
            self.after(0, lambda: self.info_label.configure(text=f"Title: {info['title']}"))
            self.after(0, lambda: self.size_label.configure(text=f"Size: ~{info['size_str']}"))
            self.after(0, lambda: self.duration_label.configure(text=f"Duration: {info['dur_str']}"))

            image = info["image"]
            if image is not None:
                ctk_img = ctk.CTkImage(light_image=image, dark_image=image, size=(180, 101))
                self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except (yt_dlp.utils.DownloadError, requests.RequestException, OSError, ValueError) as e:
            self.after(0, lambda: self.thumb_label.configure(text="Preview Error", image=""))
            self.after(0, lambda: self.status_label.configure(text=f"Preview Error: {e}"))

    def download_engine(self, url, folder, quality):
        if self.cancel_download:
            return False

        def on_progress(fraction, speed):
            self.after(0, lambda f=fraction: self.progress_bar.set(f))
            self.after(0, lambda s=speed: self.status_label.configure(text=f"Speed: {s}"))

        def on_error(error):
            self.after(0, lambda e=error: self.status_label.configure(text=f"Download Error: {e}"))

        title = download_video(
            url,
            folder,
            quality,
            is_cancelled=lambda: self.cancel_download,
            on_progress=on_progress,
            on_error=on_error,
        )
        if title is None:
            return False
        append_history(title, url)
        return True

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def open_folder(self):
        path = self.download_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Warning", "Folder tidak ditemukan!")
            return
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if url and self._is_valid_url(url):
            with self.queue_lock:
                self.queue_data.append(url)
            self.update_listbox()
            self.url_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Invalid URL!")

    def delete_selected(self):
        with self.queue_lock:
            if self.queue_data:
                self.queue_data.pop()
        self.update_listbox()

    def update_listbox(self):
        self.queue_list.delete("0.0", "end")
        with self.queue_lock:
            for i, url in enumerate(self.queue_data):
                self.queue_list.insert("end", f"{i + 1}. {url}\n")

    def process_queue(self):
        if self.is_downloading:
            return
        if not self.queue_data:
            messagebox.showwarning("Warning", "Queue kosong! Tambahkan URL terlebih dahulu.")
            return
        if not self.download_path.get():
            messagebox.showwarning("Warning", "Pilih folder download terlebih dahulu!")
            return
        self.is_downloading = True
        self.cancel_download = False
        self.btn_download.configure(state="disabled", text="DOWNLOADING...")
        self.btn_cancel.configure(state="normal")
        threading.Thread(target=self.master_download_thread, daemon=True).start()

    def cancel_active_download(self):
        if self.is_downloading:
            self.cancel_download = True
            self.status_label.configure(text="Membatalkan download...")

    def master_download_thread(self):
        folder, quality = self.download_path.get(), self.quality_box.get()
        with self.queue_lock:
            urls = list(self.queue_data)
            self.queue_data.clear()
        self.after(0, self.update_listbox)
        success, failed = 0, 0
        with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
            results = executor.map(lambda u: self.download_engine(u, folder, quality), urls)
            for r in results:
                if r:
                    success += 1
                else:
                    failed += 1
        self.after(0, lambda: self.finish_all(success, failed))

    def finish_all(self, success=0, failed=0):
        was_cancelled = self.cancel_download
        self.is_downloading = False
        self.cancel_download = False
        self.btn_download.configure(state="normal", text="Start Download")
        self.btn_cancel.configure(state="disabled")
        if was_cancelled:
            self.status_label.configure(text="Download dibatalkan.")
        elif failed == 0:
            self.status_label.configure(text=f"Selesai! {success} file berhasil diunduh.")
            messagebox.showinfo("V-DL", f"Semua download selesai! ({success} file)")
        else:
            self.status_label.configure(text=f"Selesai: {success} sukses, {failed} gagal.")
            messagebox.showwarning("V-DL", f"Download selesai.\n{success} berhasil, {failed} gagal.")

    def show_history(self):
        try:
            data = load_history()
        except (json.JSONDecodeError, OSError):
            messagebox.showinfo("History", "File history corrupt atau tidak bisa dibaca.")
            return
        if not data:
            messagebox.showinfo("History", "Belum ada riwayat download.")
            return
        build_history_window(self, data, on_clear=clear_history)
