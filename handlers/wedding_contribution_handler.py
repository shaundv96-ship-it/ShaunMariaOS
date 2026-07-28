"""
ShaunMariaOS

Wedding Contribution Handler
"""

from telegram import Update

from apps.user_engine import get_user_profile
from apps.wedding_engine import add_wedding_contribution
from apps.formatting_engine import money
from utils.logger import logger
from utils.nlp_parser import detect_wedding_contribution


async def handle_wedding_contribution(
    update: Update,
    text: str,
) -> None:
    """
    Parse and save a wedding contribution.
    """

    if not update.message or not update.effective_user:
        return

    detected = detect_wedding_contribution(text)

    if not detected:
        await update.message.reply_text(
            "❌ Unable to understand the wedding contribution."
        )
        return

    profile = get_user_profile(
        update.effective_user.id,
    )

    if profile["owner"] == "Unknown":
        await update.message.reply_text(
            "❌ This Telegram user is not registered."
        )
        return

    try:

        result = add_wedding_contribution(
            detected["amount"]
        )

        await update.message.reply_text(
            f"""💍 <b>Wedding Fund Updated</b>

👤 <b>Contributor</b>
{profile["owner"]}

💰 <b>Contribution</b>
{money(result["contribution"])}

🏦 <b>Current Savings</b>
{money(result["current_savings"])}

⚠️ <b>Remaining Shortfall</b>
{money(result["shortfall"])}""",
            parse_mode="HTML",
        )

    except Exception:
        logger.exception(
            "Failed to update wedding fund."
        )

        await update.message.reply_text(
            "⚠️ <b>Wedding Fund Not Updated</b>\n\n"
            "Something went wrong while updating Google Sheets.",
            parse_mode="HTML",
        )