"""
ShaunMariaOS

Version Engine
"""

VERSION = "v1.5 Alpha"
BUILD = "2026.07.21"

MODULES = [
    "DashboardOS",
    "MoneyOS",
    "WeddingOS",
    "CalendarOS",
    "AdvisorOS",
    "FinanceOS",
    "SalaryOS",
    "Sheets Engine",
    "Google Engine",
    "Scheduler",
]


def get_version():
    text = [
        f"🤖 <b>ShaunMariaOS {VERSION}</b>",
        "",
        f"📦 Build: {BUILD}",
        "",
        "🛠 <b>Installed Modules</b>",
        "",
    ]

    for module in MODULES:
        text.append(f"✅ {module}")

    return "\n".join(text)