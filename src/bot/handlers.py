import re
import logging
from telegram import Update
from telegram.ext import ContextTypes
from rich.console import Console

from src.bot.middlewares import owner_only
from src.bot.keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_delete_files_keyboard
)
from src.services.aria2_engine import aria2_manager
from src.services.storage_manager import storage_manager
from src.services.web_server import get_download_url
from src.utils.formatters import (
    format_bytes,
    format_speed,
    create_progress_bar,
    format_status_emoji
)

console = Console()
logger = logging.getLogger(__name__)


@owner_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk arahan /start. Memaparkan menu utama GUI secara automatik.
    """
    welcome_text = (
        "🤖 **Seedr-Lite Private Bot (V1)**\n\n"
        "Selamat datang! Gunakan butang GUI di bawah untuk menguruskan muat turun magnet "
        "dan storan OCI VM anda secara terus."
    )
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )


@owner_only
async def magnet_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk menangkap pautan Magnet dan memasukkannya ke dalam enjin aria2c.
    """
    if not update.message or not update.message.text:
        return

    raw_text = update.message.text.strip()
    
    # Ekstrak pautan magnet bersih menggunakan Regex
    magnet_match = re.search(r'(magnet:\?xt=urn:[a-zA-Z0-9:]+[^\s]*)', raw_text)

    if magnet_match:
        clean_magnet = magnet_match.group(1)
        console.print(f"[bold green]🧲 Memproses Magnet Link...[/bold green]")
        
        # Panggil enjin aria2c
        gid = aria2_manager.add_magnet(clean_magnet)

        if gid:
            reply_msg = (
                f"✅ **Magnet Link Berjaya Ditambah!**\n\n"
                f"🔑 **ID Muat Turun (GID):** `{gid}`\n"
                f"⚡ Status: Memuat turun metadata & menjejak Seeders...\n\n"
                f"Tekan butang **📊 Status Live Download** di bawah untuk semakan peratusan."
            )
        else:
            reply_msg = (
                "❌ **Ralat:** Gagal menambah pautan magnet ke daemon aria2c.\n\n"
                "Sila pastikan perkhidmatan `aria2c` di VM telah dihidupkan dengan port RPC `6800` "
                "dan `ARIA2_RPC_SECRET` di `.env.local` adalah tepat."
            )

        await update.message.reply_text(
            reply_msg,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ Mesej bukan pautan magnet yang sah. Silakan tampal pautan bermula dengan `magnet:?`",
            reply_markup=get_main_menu_keyboard()
        )


@owner_only
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Mengendalikan seluruh aliran Butang GUI Telegram (Full Interactivity).
    """
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    # 1. Navigasi Menu Utama / Refresh
    if data in ["btn_main_menu", "btn_refresh"]:
        menu_text = "🎛️ **Papan Kawalan Utama (Main Dashboard)**\n\nPilih fungsi yang dikehendaki:"
        await query.edit_message_text(
            menu_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    # 2. Bantuan Magnet
    elif data == "btn_magnet_help":
        help_text = (
            "📥 **Cara Tampal Magnet Link:**\n\n"
            "Hantar atau tampal (*paste*) pautan `magnet:?xt=urn:btih:...` terus ke dalam ruangan chat ini.\n"
            "Bot akan menangkap pautan tersebut secara automatik tanpa perlu sebarang arahan taip."
        )
        await query.edit_message_text(
            help_text,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    # 3. Status Muat Turun Real-time (Active Downloads, Seeds, Speeds)
    elif data == "btn_status":
        downloads = aria2_manager.get_all_downloads()
        
        if not downloads:
            status_text = "📊 **Status Muat Turun Live**\n\nℹ️ Tiada tugasan muat turun yang aktif buat masa ini."
        else:
            status_text = "📊 **Status Muat Turun Live**\n\n"
            for item in downloads:
                status_emoji = format_status_emoji(item["status"])
                progress_bar = create_progress_bar(item["progress"])
                completed = format_bytes(item["completed_length"])
                total = format_bytes(item["total_length"])
                speed = format_speed(item["download_speed"])

                status_text += (
                    f"📦 **{item['name']}**\n"
                    f"Status: {status_emoji}\n"
                    f"Progress: `{progress_bar}`\n"
                    f"Saiz: {completed} / {total}\n"
                    f"Kelajuan: `{speed}`\n"
                    f"🌱 Seeders: `{item['num_seeders']}` | 👥 Peers: `{item['connections']}`\n"
                    f"⏱️ ETA: `{item['eta']}`\n"
                    f"-----------------------------------\n"
                )

        await query.edit_message_text(
            status_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    # 4. Status Storan OCI VM (50GB Disk Check)
    elif data == "btn_storage":
        usage = storage_manager.get_disk_usage()
        total_str = format_bytes(usage["total_bytes"])
        used_str = format_bytes(usage["used_bytes"])
        free_str = format_bytes(usage["free_bytes"])
        progress_bar = create_progress_bar(usage["percent_used"])

        storage_text = (
            "💾 **Status Storan Disk OCI VM (50GB)**\n\n"
            f"Penggunaan: `{progress_bar}`\n"
            f"🔹 **Jumlah Ruang:** {total_str}\n"
            f"⚠️ **Digunakan:** {used_str}\n"
            f"✅ **Baki Kosong:** {free_str}\n"
        )
        await query.edit_message_text(
            storage_text,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    # 5. Senarai Fail Siap & Pautan Direct Download HTTP
    elif data == "btn_files":
        files = storage_manager.list_files()
        
        if not files:
            files_text = "📁 **Senarai Fail Sedia Ada**\n\nℹ️ Folder `downloads/` kosong."
        else:
            files_text = "📁 **Senarai Fail & Direct Download Link (HTTP):**\n\n"
            for f in files:
                size_str = format_bytes(f["size_bytes"])
                download_url = get_download_url(f["name"])
                files_text += (
                    f"📄 **{f['name']}** ({size_str})\n"
                    f"🔗 [Klik Untuk Download / IDM]({download_url})\n\n"
                )

        await query.edit_message_text(
            files_text,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    # 6. Senarai Butang Padam Fail
    elif data == "btn_delete":
        files = storage_manager.list_files()
        
        if not files:
            delete_text = "🗑️ **Padam Fail Storan**\n\nℹ️ Tiada fail untuk dipadamkan."
            await query.edit_message_text(
                delete_text,
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
        else:
            delete_text = "🗑️ **Pilih fail di bawah untuk dipadam secara kekal:**"
            await query.edit_message_text(
                delete_text,
                reply_markup=get_delete_files_keyboard(files),
                parse_mode="Markdown"
            )

    # 7. Mengendalikan Arahan Pemadaman Fail (Prefix: del_)
    elif data.startswith("del_"):
        filename_to_delete = data.replace("del_", "", 1)
        success = storage_manager.delete_file(filename_to_delete)

        if success:
            msg = f"✅ **Berjaya Dipadam:** `{filename_to_delete}`"
        else:
            msg = f"❌ **Gagal Dipadam:** Fail `{filename_to_delete}` tidak dijumpai."

        remaining_files = storage_manager.list_files()
        keyboard = get_delete_files_keyboard(remaining_files) if remaining_files else get_back_keyboard()

        await query.edit_message_text(
            msg,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )