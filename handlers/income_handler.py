"""
ShaunMariaOS

Income Handler
"""

from html import escape

from telegram import Update

from apps.income_engine import (
    parse_income,
    save_income,
)
from apps.menu_keyboard import get_persistent_main_keyboard
from apps.user_engine import get_user_profile
from utils.logger import logger


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
            (
                "❌ <b>Income Not Updated</b>\n\n"
                "Please include a valid amount.\n\n"
                "Example:\n"
                "<code>Salary 3013.80</code>"
            ),
            parse_mode="HTML",
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

    income.owner = profile["owner"]
    income.item = profile["salary_item"]

    try:
        result = save_income(income)
        finance = result["finance"]

        await update.message.reply_text(
            (
                "💰 <b>Income Updated</b>\n\n"
                f"👤 <b>Owner</b>\n"
                f"{escape(income.owner)}\n\n"
                f"💵 <b>Item</b>\n"
                f"{escape(income.item)}\n\n"
                f"💲 <b>Amount</b>\n"
                f"${income.amount:,.2f}\n\n"
                f"🏦 <b>Available Money</b>\n"
                f"${finance['available']:,.2f}\n\n"
                "📊 MoneyOS is now up to date."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception as error:
        logger.exception(
            "Failed to update income."
        )

        await update.message.reply_text(
            (
                "❌ <b>Income Not Updated</b>\n\n"
                f"{escape(str(error))}"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )