"""
Shaun&Maria OS
Configuration Module

This module loads all application settings.
"""

from dotenv import load_dotenv
import os

# Load variables from the .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")