from pathlib import Path
from urllib.parse import quote
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from rich.console import Console

from src.config import settings

console = Console()

# Inisialisasi pelayan FastAPI
app = FastAPI(
    title="Seedr-Lite Direct Download Server",
    description="Pelayan HTTP statik untuk muat turun terus ke IDM",
    version="1.0.0"
)

# Memastikan folder downloads/ wujud sebelum dipetakan
download_path = Path(settings.DOWNLOAD_DIR).resolve()
download_path.mkdir(parents=True, exist_ok=True)

# Pemetaan Pelayan Fail Statik (Static Files Mount)
# Membolehkan akses fail via: http://SERVER_DOMAIN/downloads/nama_fail.mkv
app.mount(
    "/downloads",
    StaticFiles(directory=str(download_path), html=False),
    name="downloads"
)


@app.get("/")
async def health_check():
    """
    Endpoint asas untuk menyemak status pelayan web FastAPI.
    """
    return JSONResponse({
        "status": "online",
        "service": "Seedr-Lite Web Server",
        "download_endpoint": f"{settings.SERVER_DOMAIN}/downloads/"
    })


def get_download_url(filename: str) -> str:
    """
    Menjana pautan direct HTTP URL yang diselaraskan dengan URL encoding
    supaya IDM boleh memuat turun fail dengan nama khas/ruang kosong dengan lancar[cite: 1].
    """
    encoded_filename = quote(filename)
    base_url = settings.SERVER_DOMAIN.rstrip("/")
    return f"{base_url}/downloads/{encoded_filename}"