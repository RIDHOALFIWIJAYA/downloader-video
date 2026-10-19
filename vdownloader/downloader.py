import os
import re

import yt_dlp


def _build_options(folder, quality, hook):
    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "progress_hooks": [hook],
        "quiet": True,
        "writethumbnail": True,
        "continuedl": True,
        "postprocessors": [{"key": "FFmpegMetadata"}, {"key": "EmbedThumbnail"}],
    }

    if "720p" in quality:
        ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
    elif "480p" in quality:
        ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"
    elif "Audio" in quality:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"].insert(
            0, {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
        )
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    return ydl_opts


def download_video(url, folder, quality, *, is_cancelled, on_progress, on_error):
    def hook(d):
        if is_cancelled():
            raise yt_dlp.utils.DownloadError("Cancelled by user")
        if d["status"] == "downloading":
            p_str = d.get("_percent_str", "0%")
            clean_p = re.sub(r"\x1b\[[0-9;]*m", "", p_str).replace("%", "").strip()
            try:
                on_progress(float(clean_p) / 100, d.get("_speed_str", "N/A"))
            except ValueError:
                pass

    ydl_opts = _build_options(folder, quality, hook)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url, download=True)
            return meta.get("title", "Unknown")
    except (yt_dlp.utils.DownloadError, OSError, ValueError) as e:
        if not is_cancelled():
            on_error(e)
        return None
