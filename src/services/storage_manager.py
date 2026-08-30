import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console

from src.config import settings

console = Console()
logger = logging.getLogger(__name__)


class StorageManager:
    """
    Menguruskan pengesyoran disk tempatan 50GB OCI VM dan operasi penfailan[cite: 1].
    """
    def __init__(self):
        self.download_path = Path(settings.DOWNLOAD_DIR).resolve()
        # Memastikan folder downloads/ wujud secara automatik
        self.download_path.mkdir(parents=True, exist_ok=True)

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Membaca statistik baki dan penggunaan ruang disk VM (50GB)[cite: 1].
        """
        total, used, free = shutil.disk_usage(self.download_path)
        percent_used = (used / total) * 100

        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "percent_used": round(percent_used, 2)
        }

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Menyenaraikan semua fail dan folder yang berada di dalam downloads/[cite: 1].
        """
        files_list = []
        if not self.download_path.exists():
            return files_list

        for item in self.download_path.iterdir():
            # Abaikan fail tersembunyi seperti .gitkeep
            if item.name.startswith("."):
                continue

            size = 0
            if item.is_file():
                size = item.stat().st_size
            elif item.is_dir():
                size = sum(f.stat().st_size for f in item.glob('**/*') if f.is_file())

            files_list.append({
                "name": item.name,
                "path": str(item),
                "size_bytes": size,
                "is_dir": item.is_dir(),
                "mtime": item.stat().st_mtime
            })

        # Susun fail mengikut masa kemaskini terkini (paling baru di atas)
        files_list.sort(key=lambda x: x["mtime"], reverse=True)
        return files_list

    def delete_file(self, filename: str) -> bool:
        """
        Memadam fail atau folder secara kekal dari disk VM apabila diminta dari Telegram[cite: 1].
        """
        target_path = (self.download_path / filename).resolve()

        # Kawalan Keselamatan Path Traversal (Cari sasaran hanya di dalam DOWNLOAD_DIR)
        if not str(target_path).startswith(str(self.download_path)):
            logger.warning(f"Percubaan pemadaman luar dari julat kebenaran: {target_path}")
            return False

        if not target_path.exists():
            logger.warning(f"Fail tidak dijumpai untuk dipadam: {target_path}")
            return False

        try:
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)

            console.print(f"[bold red]🗑️ Fail Dipadam Secara Kekal:[/bold red] {filename}")
            return True
        except Exception as e:
            logger.error(f"Gagal memadam fail {filename}: {e}")
            return False


# Singleton instance untuk digunakan di seluruh modul bot
storage_manager = StorageManager()