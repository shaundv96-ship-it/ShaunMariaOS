"""
ShaunMariaOS

Task Handler
"""

from html import escape

from telegram import Update

from apps.menu_keyboard import get_persistent_main_keyboard
from apps.task_engine import (
    complete_task,
    get_open_tasks,
    parse_task,
    parse_task_completion,
    save_task,
)
from apps.user_engine import get_user_profile
from utils.logger import logger


def get_tasks_message() -> str:
    """Build the open-task dashboard."""

    tasks = get_open_tasks()

    if not tasks:
        return (
            "📋 <b>Open Tasks</b>\n\n"
            "✅ There are no open tasks."
        )

    sections = [
        "📋 <b>Open Tasks</b>",
    ]

    for task in tasks:
        task_text = escape(task["task"])
        owner = escape(task["owner"])
        priority = escape(task["priority"])

        sections.append(
            f"\n\n<b>{task['id']}. {task_text}</b>"
            f"\n👤 {owner}"
            f"\n📌 {priority}"
        )

        if task["due_date"]:
            sections.append(
                f"\n📅 {escape(task['due_date'])}"
            )

    sections.append(
        "\n\nComplete a task with:"
        "\n<code>Done 1</code>"
    )

    return "".join(sections)


async def handle_task(
    update: Update,
    text: str,
) -> None:
    """Add or complete a natural-language task."""

    if not update.message or not update.effective_user:
        return

    completion_id = parse_task_completion(text)

    if completion_id is not None:
        try:
            completed = complete_task(completion_id)

            await update.message.reply_text(
                (
                    "✅ <b>Task Completed</b>\n\n"
                    f"📝 {escape(completed['task'])}"
                ),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )

        except ValueError as error:
            await update.message.reply_text(
                f"⚠️ {escape(str(error))}",
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )

        except Exception:
            logger.exception("Failed to complete task.")

            await update.message.reply_text(
                "⚠️ <b>Task Not Updated</b>\n\n"
                "Something went wrong while updating Google Sheets.",
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )

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
                f"📝 <b>Task</b>\n{escape(task.task)}\n\n"
                f"👤 <b>Owner</b>\n{escape(task.owner)}\n\n"
                f"📌 <b>Priority</b>\n"
                f"{escape(task.priority)}\n\n"
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