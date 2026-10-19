import json
import os
from datetime import datetime

from .config import HISTORY_FILE


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return None
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def append_history(title, url):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = []
    data.append({
        "title": title,
        "url": url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def clear_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)


def format_history(data, limit=20):
    lines = []
    for i, entry in enumerate(data[-limit:], 1):
        lines.append(
            f"{i}. {entry.get('title', '?')}\n"
            f"   {entry.get('timestamp', '?')}\n"
            f"   {entry.get('url', '?')}"
        )
    return "\n\n".join(lines)
