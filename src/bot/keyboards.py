from typing import List, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Menjana papan kekunci utama (Main GUI Menu) Telegram Bot.
    """
    keyboard = [
        [
            InlineKeyboardButton("📥 Cara Tampal Magnet", callback_data="btn_magnet_help"),
            InlineKeyboardButton("📊 Status Live Download", callback_data="btn_status"),
        ],
        [
            InlineKeyboardButton("💾 Status Storan (50GB)", callback_data="btn_storage"),
            InlineKeyboardButton("📁 Fail & Link HTTP", callback_data="btn_files"),
        ],
        [
            InlineKeyboardButton("🗑️ Urus & Padam Fail", callback_data="btn_delete"),
            InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="btn_refresh"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Papan kekunci navigasi Kembali ke Menu Utama.
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Kembali ke Menu Utama", callback_data="btn_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_delete_files_keyboard(files: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Menjana butang GUI dinamik bagi setiap fail yang sedia ada untuk pemadaman mudah.
    """
    keyboard = []
    for f in files:
        filename = f["name"]
        # Potong nama fail jika terlalu panjang untuk paparan butang Telegram
        display_name = filename if len(filename) <= 25 else filename[:22] + "..."
        keyboard.append([
            InlineKeyboardButton(f"❌ {display_name}", callback_data=f"del_{filename}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Kembali ke Menu Utama", callback_data="btn_main_menu")])
    return InlineKeyboardMarkup(keyboard)