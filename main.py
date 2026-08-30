import asyncio
import logging
import uvicorn
from rich.console import Console

from src.config import settings
from src.services.web_server import app as fastapi_app
from src.bot.main import build_bot_application

# Eksport 'app' di peringkat modul supaya ASGI runner boleh mencarinya
app = fastapi_app

console = Console()
logger = logging.getLogger(__name__)


async def run_services():
    """
    Menjalankan Pelayan Web FastAPI (Uvicorn) dan Telegram Bot 
    secara serentak di dalam satu Asyncio Event Loop.
    """
    # 1. Konfigurasi Pelayan FastAPI (Uvicorn)
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)

    # 2. Inisialisasi Telegram Bot
    bot_app = build_bot_application()

    console.print(
        f"[bold green]🚀 Memulakan Seedr-Lite Engine...[/bold green]\n"
        f"🌐 [cyan]FastAPI Direct Download:[/cyan] {settings.SERVER_DOMAIN}/downloads/\n"
        f"🤖 [cyan]Telegram Bot Owner ID:[/cyan] {settings.TELEGRAM_CHAT_ID}"
    )

    # 3. Jalankan kedua-dua perkhidmatan secara serentak
    async with bot_app:
        await bot_app.start()
        await bot_app.updater.start_polling()
        
        # Jalankan pelayan FastAPI
        await server.serve()

        # Pembersihan perkhidmatan semasa bot dihentikan
        await bot_app.updater.stop()
        await bot_app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(run_services())
    except (KeyboardInterrupt, SystemExit):
        console.print("\n[bold yellow]🛑 Perkhidmatan Seedr-Lite dihentikan secara manual.[/bold yellow]")