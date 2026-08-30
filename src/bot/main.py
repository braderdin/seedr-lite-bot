import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from rich.console import Console

from src.config import settings
from src.bot.handlers import start_command, button_callback_handler, magnet_message_handler

console = Console()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def build_bot_application() -> Application:
    """
    Membina dan mendaftarkan semua handler untuk Telegram Bot Application[cite: 1].
    """
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Pendaftaran Handler Arahan & GUI
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    # Pendaftaran Handler Mesej Teks (Magnet link)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, magnet_message_handler)
    )

    return application


async def run_bot_async():
    """
    Fungsi untuk menjalankan bot secara asynchronous (Long Polling untuk V1)[cite: 1].
    """
    app = build_bot_application()
    console.print("[bold cyan]🚀 Memulakan Telegram Bot (Long Polling)...[/bold cyan]")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()