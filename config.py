"""
ShaunMariaOS

Configuration Module
Loads external service settings from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing.")

if not GOOGLE_CALENDAR_ID:
    raise ValueError("GOOGLE_CALENDAR_ID environment variable is missing.")

if not GOOGLE_SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID environment variable is missing.")

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]