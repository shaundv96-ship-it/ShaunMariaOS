"""
ShaunMariaOS

Income Handler
"""

from telegram import Update

from apps.income_engine import (
    parse_income,
    save_income,
)
from apps.user_engine import get_user_profile


async def handle_income(
    update: Update,
    text: str,
) -> None:
    """Parse and save an income update."""

    if not update.message or not update.effective_user:
        return

    income = parse_income(text)

    if income is None:
        await update.message.reply_text(
            "❌ Unable to understand the income amount.",
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

    income.owner = profile["owner"]
    income.item = profile["salary_item"]

    try:
        save_income(income)

        await update.message.reply_text(
            (
                "💰 <b>Income Updated</b>\n\n"
                f"👤 <b>Owner</b>\n{income.owner}\n\n"
                f"💵 <b>Item</b>\n{income.item}\n\n"
                f"💲 <b>Amount</b>\n"
                f"${income.amount:,.2f}\n\n"
                "📊 Finance sheet updated."
            ),
            parse_mode="HTML",
        )

    except Exception as error:
        await update.message.reply_text(
            f"❌ {error}"
        )