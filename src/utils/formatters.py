from typing import Union


def format_bytes(size_in_bytes: Union[float, int]) -> str:
    """
    Menukar angka bait mentah (bytes) kepada format saiz mudah dibaca (KB, MB, GB, TB)[cite: 1].
    """
    if not size_in_bytes or size_in_bytes <= 0:
        return "0.00 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_in_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.2f} {units[i]}"


def format_speed(bytes_per_sec: Union[float, int]) -> str:
    """
    Memformat kelajuan muat turun kepada unit per saat (cth: 5.40 MB/s).
    """
    return f"{format_bytes(bytes_per_sec)}/s"


def create_progress_bar(percent: float, length: int = 10) -> str:
    """
    Menjana bar kemajuan visual teks untuk kegunaan GUI Telegram (cth: [██████░░░░] 60.0%)[cite: 1].
    """
    percent = max(0.0, min(100.0, percent))
    filled_length = int(round(length * percent / 100))
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}] {percent:.1f}%"


def format_status_emoji(status: str) -> str:
    """
    Menukar status mentah aria2c kepada bentuk emoji dan bahasa Melayu yang kemas.
    """
    mapping = {
        "active": "⚡ Sedang Muat Turun",
        "waiting": "⏳ Dalam Barisan",
        "paused": "⏸️ Dihentikan",
        "complete": "✅ Siap 100%",
        "error": "❌ Ralat",
        "removed": "🗑️ Dipadam"
    }
    return mapping.get(status.lower(), f"ℹ️ {status.capitalize()}")