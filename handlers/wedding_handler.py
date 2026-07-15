"""
ShaunMariaOS

Wedding Handler
"""

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard


async def handle_wedding(
    update: Update,
    text: str,
) -> None:
    """Handle natural-language wedding messages."""

    if not update.message:
        return

    await update.message.reply_text(
        "💍 <b>Wedding-related message detected</b>\n\n"
        "For now, record wedding payments as ordinary "
        "expenses using wording such as:\n\n"
        "<code>Florist $500</code>",
        parse_mode="HTML",
        reply_markup=get_persistent_main_keyboard(),
    )