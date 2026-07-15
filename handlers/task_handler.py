"""
ShaunMariaOS

Task Handler
"""

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard


async def handle_task(
    update: Update,
    text: str,
) -> None:
    """Handle task-related messages until TaskOS is connected."""

    if not update.message:
        return

    await update.message.reply_text(
        "✅ <b>Task detected</b>\n\n"
        "Task logging will be connected later.",
        parse_mode="HTML",
        reply_markup=get_persistent_main_keyboard(),
    )