"""
ShaunMariaOS

Inline Menu Buttons
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_buttons():
    keyboard = [
        [
            InlineKeyboardButton("📅 Today", callback_data="menu_today"),
            InlineKeyboardButton("💍 Wedding", callback_data="menu_wedding"),
        ],
        [
            InlineKeyboardButton("💰 Money", callback_data="menu_money"),
            InlineKeyboardButton("❤️ Dashboard", callback_data="menu_dashboard"),
        ],
        [
            InlineKeyboardButton("⚙️ System", callback_data="menu_system"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)