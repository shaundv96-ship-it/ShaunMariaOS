"""
ShaunMariaOS

Telegram Menu Keyboard
"""

from telegram import ReplyKeyboardMarkup


def get_main_keyboard():
    keyboard = [
        ["📅 Today", "💍 Wedding"],
        ["💰 Money", "🏠 Home"],
        ["❤️ Dashboard", "⚙️ More"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )