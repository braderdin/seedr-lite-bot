from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Jalur direktori utama projek (Root Directory)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Menguruskan semua pembolehubah alam sekitar (.env.local & GitHub Secrets).
    """
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int
    TELEGRAM_BOT_LINK: Optional[str] = None

    # Aria2 RPC Configuration
    ARIA2_RPC_HOST: str = "http://127.0.0.1"
    ARIA2_RPC_PORT: int = 6800
    ARIA2_RPC_SECRET: str = ""

    # FastAPI Server Configuration
    PORT: int = 8000
    SERVER_DOMAIN: str = "http://168.107.64.203:8000"
    DOWNLOAD_DIR: str = "./downloads"

    # OCI & Encryption Keys
    GPG_PASSPHRASE: Optional[str] = None
    OCI_HOST: Optional[str] = "168.107.64.203"
    OCI_USERNAME: Optional[str] = "ubuntu"
    OCI_SUBNET_ID: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def download_path(self) -> Path:
        """Mengembalikan Path mutlak untuk folder muat turun."""
        path = Path(self.DOWNLOAD_DIR)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    def is_owner(self, user_id: int) -> bool:
        """
        Menyemak adakah User ID Telegram yang menghantar arahan 
        sepadan dengan TELEGRAM_CHAT_ID pemunya.
        """
        return user_id == self.TELEGRAM_CHAT_ID


# Singleton instance untuk diguna pakai di seluruh modul projek
settings = Settings()