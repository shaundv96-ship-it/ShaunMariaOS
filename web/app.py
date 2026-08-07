"""
ShaunMariaOS

Web Application
API and web interface for ShaunMariaOS.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.money_service import get_money_overview
from core.calendar_service import get_today_events
from core.money_service import get_money_overview

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ShaunMariaOS",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
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

@app.get("/api/calendar/today")
def calendar_today():
    """Return today's CalendarOS events."""

    result = get_today_events()

    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "events": result.events,
    }

@app.get("/")
def dashboard(
    request: Request,
):
    """Render the ShaunMariaOS dashboard."""

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page_title": "Home",
        },
    )

