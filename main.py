"""
Shaun&Maria OS
Main Application Entry Point
"""

from config import BOT_TOKEN, CHAT_ID, OPENAI_API_KEY, GOOGLE_CALENDAR_ID


def show_startup_status():
    print("=" * 40)
    print("❤️ Shaun&Maria OS v0.1")
    print("=" * 40)
    print()

    print("System Check:")

    print("BOT_TOKEN:", "✅ Loaded" if BOT_TOKEN else "❌ Missing")
    print("CHAT_ID:", "✅ Loaded" if CHAT_ID else "❌ Missing")
    print("OPENAI_API_KEY:", "✅ Loaded" if OPENAI_API_KEY else "⚪ Not set yet")
    print("GOOGLE_CALENDAR_ID:", "✅ Loaded" if GOOGLE_CALENDAR_ID else "⚪ Not set yet")

    print()
    print("Status: System foundation ready.")


if __name__ == "__main__":
    show_startup_status()