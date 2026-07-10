#  V-Downloader

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-CustomTkinter-orange.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Backend](https://img.shields.io/badge/Engine-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)

**V-Downloader** adalah aplikasi desktop GUI modern untuk mendownload video dari berbagai platform (YouTube, dll) dengan fokus pada kemudahan penggunaan, kualitas video yang presisi, dan manajemen file yang rapi.

---

## ✨ Fitur Unggulan

* **🎨 Modern UI:** Interface bersih dan responsif menggunakan `CustomTkinter`.
* **🖼️ Live Preview:** Menampilkan thumbnail video secara real-time sebelum didownload.
* **📊 Smart Info:** Estimasi ukuran file (Size) dan durasi video otomatis.
* **🏷️ Auto-Metadata:** Menanamkan Judul, Artist, dan Thumbnail (Cover Art) langsung ke dalam file MP4/MP3.
* **🎞️ Quality Selector:** Pilih resolusi 720p, 480p, atau **Audio Only (MP3)** dengan format H.264 (AVC) yang kompatibel di semua device.
* **📜 History Manager:** Riwayat download tersimpan dalam `history.json` dan bisa dilihat langsung melalui UI aplikasi.
* **🚀 Queue System:** Tambahkan banyak link ke antrean dan biarkan aplikasi menyelesaikannya satu per satu.
* **🌐 Parallel Download:** Downloads up to 2 videos simultaneously using a thread pool for faster batch processing.


---

## 📸 Preview Aplikasi

<p align="center">
  <img src="https://github.com/user-attachments/assets/4390ce10-697d-46a4-983f-e3ce22bfa69a" alt="V-DL PRO Screenshot" width="800">
</p>

---

## 🛠️ Persyaratan Sistem

Sebelum menjalankan, pastikan perangkat Anda sudah terinstall:

1.  **Python 3.10+**
2.  **FFmpeg:** Wajib ada agar fitur penggabungan video/audio dan penulisan metadata (Cover Art) berfungsi.
    * *Tips: Ensure ffmpeg is installed on your system (e.g., `sudo apt install ffmpeg`) or specify its path.*

---

## 🚀 Cara Instalasi & Penggunaan

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/RIDHOALFIWIJAYA/downloader-video.git
    cd downloader-video
    ```

2.  **Install Dependensi:**
    ```bash
    pip install customtkinter yt-dlp requests Pillow
    ```

3.  **Jalankan Aplikasi:**
    ```bash
    python main.py
    ```

---

## 📈 Log Update

### 🆕 Update v5.4 (Latest)
- Added theme switcher (Dark, Light, System mode).
- Linux-optimized stable release with full UI compatibility.

### 🆕 Update v5.3
- UI overhaul for Linux compatibility.
- Improved sidebar layout and widget styling.

### 🆕 Update v5.0
- Penambahan fitur **Size Estimation** (Estimasi ukuran file).
- Fitur **Auto-Tagging**: Otomatis menyematkan thumbnail sebagai cover art pada file.
- Penambahan info durasi video.

### 🆕 Update v5.1
- Penambahan logic untuk **Parallel Download**.
- Dan improvement beberapa logic di app.

### 🆕 Update v5.2
- penambahan fitur untuk otomatis menyalin dari clipboard.
  **Note pastikan untuk menyalin tautan video terlebih dahulu setelah itu baru jalankan appnya.**

---

## 🤝 Kontribusi
Punya ide fitur keren? Silakan buka *Issue* atau kirim *Pull Request*!

**Dibuat dengan ❤️ oleh [RidhoAlfiWijaya](https://github.com/RIDHOALFIWIJAYA)**
