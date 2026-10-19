from io import BytesIO

import requests
import yt_dlp
from PIL import Image


def fetch_video_info(url):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title")
    filesize = info.get("filesize") or info.get("filesize_approx")
    duration = info.get("duration")
    size_str = f"{filesize / (1024 * 1024):.1f} MB" if filesize else "Unknown"
    dur_str = f"{duration // 60}m {duration % 60}s" if duration else "-"

    image = None
    thumb_url = info.get("thumbnail")
    if thumb_url:
        resp = requests.get(thumb_url, timeout=10)
        image = Image.open(BytesIO(resp.content))

    return {
        "title": title,
        "size_str": size_str,
        "dur_str": dur_str,
        "image": image,
    }
