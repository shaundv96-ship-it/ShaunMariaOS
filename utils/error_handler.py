"""
Global Error Handler
"""

from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import logger


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    logger.exception(context.error)

    if isinstance(update, Update) and update.effective_message:

        await update.effective_message.reply_text(

            "⚠️ Something went wrong.\n\n"
            "ShaunMariaOS has logged the error.\n"
            "Please try again."

        )