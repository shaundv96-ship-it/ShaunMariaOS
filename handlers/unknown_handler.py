"""
ShaunMariaOS

Unknown Message Handler
"""

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard


async def handle_unknown(
    update: Update,
    text: str,
) -> None:
    """Handle messages with no recognised intent."""

    if not update.message:
        return

    await update.message.reply_text(
        "I’m not sure what you’d like me to do with that yet.",
        reply_markup=get_persistent_main_keyboard(),
    )