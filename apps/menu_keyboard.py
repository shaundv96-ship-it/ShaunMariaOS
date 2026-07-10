"""
ShaunMariaOS

Inline Menu Buttons
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_buttons():
    return InlineKeyboardMarkup([
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
    ])


def get_wedding_menu_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Budget", callback_data="wedding_budget"),
            InlineKeyboardButton("👥 Guest List", callback_data="wedding_guestlist"),
        ],
        [
            InlineKeyboardButton("📅 Timeline", callback_data="wedding_timeline"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main"),
        ],
    ])


def get_money_menu_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💰 Overview",
                callback_data="money_overview",
            ),
        ],
        [
            InlineKeyboardButton(
                "💵 Salary",
                callback_data="money_salary",
            ),
            InlineKeyboardButton(
                "🧾 Bills",
                callback_data="money_bills",
            ),
        ],
        [
            InlineKeyboardButton(
                "🛡 Insurance",
                callback_data="money_insurance",
            ),
        ],
        [
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="menu_main",
            ),
        ],
    ])


def get_system_menu_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❤️ Health", callback_data="menu_system"),
            InlineKeyboardButton("🚀 Version", callback_data="system_version"),
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="system_about"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main"),
        ],
    ])