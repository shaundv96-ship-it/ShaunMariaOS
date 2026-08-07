"""
ShaunMariaOS

Web Application
Local API and web interface for ShaunMariaOS.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from core.money_service import get_money_overview


app = FastAPI(
    title="ShaunMariaOS",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Confirm that ShaunMariaOS Web is running."""

    return {
        "status": "online",
        "system": "ShaunMariaOS",
        "version": "0.1.0",
    }


@app.get("/api/money")
def money_overview():
    """Return structured MoneyOS data."""

    result = get_money_overview()

    return {
        "success": result.success,
        "status": result.status,
        "income": result.income,
        "expenses": result.expenses,
        "allocated": result.allocated,
        "monthly_cash_flow": result.monthly_cash_flow,
        "available_money": result.available_money,
        "savings": result.savings,
        "bills": result.bills,
        "insurance": result.insurance,
        "health": result.health,
    }


@app.get("/", response_class=HTMLResponse)
def home():
    """Render the first ShaunMariaOS screen."""

    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>ShaunMariaOS</title>

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
            >

            <style>
                body {
                    font-family:
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;

                    margin: 0;
                    background: #f6f6f8;
                    color: #1d1d1f;
                }

                .container {
                    max-width: 480px;
                    margin: 0 auto;
                    padding: 32px 20px;
                }

                .brand {
                    font-size: 14px;
                    font-weight: 700;
                    opacity: 0.55;
                }

                h1 {
                    margin-top: 8px;
                    font-size: 34px;
                    line-height: 1.1;
                }

                .subtitle {
                    color: #666;
                    line-height: 1.5;
                }

                .card {
                    margin-top: 24px;
                    padding: 22px;
                    background: white;
                    border-radius: 24px;
                    box-shadow:
                        0 8px 30px
                        rgba(0, 0, 0, 0.06);
                }

                .status {
                    display: inline-block;
                    margin-top: 12px;
                    padding: 7px 12px;
                    border-radius: 999px;
                    background: #e7f7ec;
                    color: #18733c;
                    font-size: 13px;
                    font-weight: 700;
                }

                .heart {
                    font-size: 36px;
                }
            </style>
        </head>

        <body>
            <main class="container">

                <div class="brand">
                    SHAUNMARIAOS
                </div>

                <h1>
                    Good afternoon,<br>
                    Shaun & Maria.
                </h1>

                <p class="subtitle">
                    Your life, money, calendar and plans —
                    finally in one place.
                </p>

                <section class="card">

                    <div class="heart">
                        ❤️
                    </div>

                    <h2>
                        ShaunMariaOS is online.
                    </h2>

                    <p>
                        CalendarOS and MoneyOS Core are
                        ready for the new app.
                    </p>

                    <span class="status">
                        ● SYSTEM HEALTHY
                    </span>

                </section>

            </main>
        </body>
    </html>
    """