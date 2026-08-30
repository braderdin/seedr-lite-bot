import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from rich.console import Console

from src.config import settings

console = Console()
logger = logging.getLogger(__name__)


def owner_only(func):
    """
    Middleware / Decorator keselamatan Telegram Bot.
    Menyemak user.id secara automatik sebelum menjalankan sebarang handler atau butang GUI.
    Jika user.id bukan TELEGRAM_CHAT_ID, arahan akan diabaikan secara senyap (Privacy Gatekeeper).
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        if not user:
            return

        # Semakan keselamatan ID
        if not settings.is_owner(user.id):
            console.print(
                f"[bold red]⛔ ACCESS DENIED:[/bold red] Unverified attempt from "
                f"[yellow]{user.full_name}[/yellow] (ID: [cyan]{user.id}[/cyan])"
            )
            logger.warning(
                f"Akses ditolak untuk User ID: {user.id} ({user.full_name}). "
                f"Hanya Owner ID ({settings.TELEGRAM_CHAT_ID}) dibenarkan."
            )
            
            # Jika arahan datang dari butang GUI (CallbackQuery), matikan status loading butang
            if update.callback_query:
                await update.callback_query.answer("⛔ Akses Ditolak!", show_alert=True)
                
            return  # Hentikan pelaksanaan kod jika bukan owner

        return await func(update, context, *args, **kwargs)

    return wrapper