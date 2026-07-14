"""
ShaunMariaOS

Expense Handler
"""

from telegram import Update

from apps.expense_engine import (
    ExpenseEntry,
    detect_category,
    format_expense_confirmation,
    save_expense,
)
from apps.user_engine import get_user_profile
from utils.logger import logger
from utils.nlp_parser import detect_expense


async def handle_expense(
    update: Update,
    text: str,
) -> None:
    """Parse and save a natural-language expense."""

    if not update.message or not update.effective_user:
        return

    detected = detect_expense(text)

    if not detected:
        await update.message.reply_text(
            "❌ Unable to understand the expense.",
        )
        return

    profile = get_user_profile(
        update.effective_user.id,
    )

    if profile["owner"] == "Unknown":
        await update.message.reply_text(
            "❌ This Telegram user is not registered.",
        )
        return

    expense = ExpenseEntry(
        amount=detected["amount"],
        item=detected["item"],
        category=detect_category(
            detected["item"],
        ),
        owner=profile["owner"],
    )

    try:
        save_expense(expense)

        await update.message.reply_text(
            format_expense_confirmation(expense),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception(
            "Failed to save natural-language expense."
        )

        await update.message.reply_text(
            "⚠️ <b>Expense Not Added</b>\n\n"
            "Something went wrong while updating Google Sheets.",
            parse_mode="HTML",
        )