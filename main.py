"""
Shaun&Maria OS
Main Application Entry Point
"""

from bot.telegram_bot import send_message


def main():
    message = """❤️ <b>Shaun&Maria OS v0.2</b>

✅ Telegram Engine Online
✅ Python Connected
✅ System Ready"""

    result = send_message(message)
    print(result)


if __name__ == "__main__":
    main()