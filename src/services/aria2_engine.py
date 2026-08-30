import logging
from typing import List, Dict, Any, Optional
import aria2p
from rich.console import Console

from src.config import settings

console = Console()
logger = logging.getLogger(__name__)


class Aria2Manager:
    """
    Menguruskan komunikasi RPC dengan daemon aria2c menggunakan perpustakaan aria2p.
    """
    def __init__(self):
        self._client = aria2p.Client(
            host=settings.ARIA2_RPC_HOST,
            port=settings.ARIA2_RPC_PORT,
            secret=settings.ARIA2_RPC_SECRET
        )
        self.aria2 = aria2p.API(self._client)

    def add_magnet(self, magnet_uri: str) -> Optional[str]:
        """
        Menambah pautan magnet ke dalam barisan muat turun aria2c.
        Mengembalikan GID jika berjaya.
        """
        try:
            # Pastikan folder muat turun wujud dan tetapkan lokasi simpanan aria2
            download_dir = str(settings.download_path)
            options = {"dir": download_dir}

            download = self.aria2.add_magnet(magnet_uri, options=options)
            console.print(f"[bold green]✅ Magnet Berjaya Ditambah:[/bold green] GID {download.gid}")
            return download.gid
        except Exception as e:
            logger.error(f"Gagal menambah pautan magnet ke aria2: {e}", exc_info=True)
            console.print(f"[bold red]❌ Ralat Aria2 RPC:[/bold red] {e}")
            return None

    def get_all_downloads(self) -> List[Dict[str, Any]]:
        """
        Mengambil status real-time semua muat turun (Active, Waiting, Complete).
        """
        try:
            downloads = self.aria2.get_downloads()
            results = []
            for dl in downloads:
                num_seeders = getattr(dl, "num_seeders", 0)
                connections = getattr(dl, "connections", 0)

                results.append({
                    "gid": dl.gid,
                    "name": dl.name or "Memuat turun metadata magnet...",
                    "status": dl.status,  # active, waiting, paused, error, complete
                    "total_length": dl.total_length,  # Saiz asal dalam bait
                    "completed_length": dl.completed_length,  # Bait selesai
                    "download_speed": dl.download_speed,  # Kelajuan (bytes/s)
                    "progress": dl.progress,  # Peratusan (0.00 - 100.00)
                    "eta": dl.eta_string(),  # Anggaran masa siap
                    "num_seeders": num_seeders,
                    "connections": connections,
                    "is_complete": dl.is_complete,
                })
            return results
        except Exception as e:
            logger.error(f"Gagal mengambil status muat turun dari aria2: {e}")
            return []

    def remove_download(self, gid: str, force: bool = True) -> bool:
        """
        Membatalkan atau memadam tugas muat turun dari barisan aria2c mengikut GID.
        """
        try:
            download = self.aria2.get_download(gid)
            download.remove(force=force, files=True)
            console.print(f"[yellow]🗑️ Tugas GID {gid} dipadam dari aria2c[/yellow]")
            return True
        except Exception as e:
            logger.error(f"Gagal memadam GID {gid}: {e}")
            return False


# Singleton instance untuk digunakan di seluruh modul bot
aria2_manager = Aria2Manager()