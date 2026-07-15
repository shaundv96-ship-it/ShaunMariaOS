"""
ShaunMariaOS

Task Handler
"""

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard
from apps.task_engine import (
    parse_task,
    save_task,
)
from apps.user_engine import get_user_profile
from utils.logger import logger


async def handle_task(
    update: Update,
    text: str,
) -> None:
    """Parse and save a natural-language task."""

    if not update.message or not update.effective_user:
        return

    task = parse_task(text)

    if task is None:
        await update.message.reply_text(
            "❌ Unable to understand the task.",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    profile = get_user_profile(
        update.effective_user.id,
    )

    if profile["owner"] == "Unknown":
        await update.message.reply_text(
            "❌ This Telegram user is not registered.",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    task.owner = profile["owner"]

    try:
        save_task(task)

        await update.message.reply_text(
            (
                "✅ <b>Task Added</b>\n\n"
                f"📝 <b>Task</b>\n{task.task}\n\n"
                f"👤 <b>Owner</b>\n{task.owner}\n\n"
                f"📌 <b>Priority</b>\n{task.priority}\n\n"
                "📋 Task list updated."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception("Failed to save task.")

        await update.message.reply_text(
            "⚠️ <b>Task Not Added</b>\n\n"
            "Something went wrong while updating Google Sheets.",
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )