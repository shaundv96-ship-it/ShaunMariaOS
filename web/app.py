"""
ShaunMariaOS

Web Application
API and web interface for ShaunMariaOS.
"""

from pathlib import Path
from datetime import date
from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.money_service import get_money_overview
from core.calendar_service import (
    create_event_from_text,
    get_events_for_date,
    get_today_events,
)
from core.money_service import get_money_overview
from core.task_service import (
    complete_task_by_id,
    create_task_from_text,
    get_tasks,
)


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

class CalendarCreateRequest(BaseModel):
    """Natural-language CalendarOS creation request."""

    text: str

class TaskCreateRequest(BaseModel):
    """Natural-language task creation request."""

    text: str

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

@app.get("/api/calendar/date/{date_text}")
def calendar_by_date(
    date_text: str,
):
    """Return CalendarOS events for one date."""

    try:
        target_date = date.fromisoformat(
            date_text
        )

    except ValueError:
        return {
            "success": False,
            "status": "invalid_date",
            "message": (
                "Date must use YYYY-MM-DD format."
            ),
            "events": [],
        }

    result = get_events_for_date(
        target_date
    )

    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "date": target_date.isoformat(),
        "events": result.events,
    }

@app.get("/calendar")
def calendar_page(
    request: Request,
):
    """Render CalendarOS."""

    return templates.TemplateResponse(
        request=request,
        name="calendar.html",
        context={
            "page_title": "Calendar",
        },
    )
@app.post("/api/calendar/create")
def calendar_create(
    request: CalendarCreateRequest,
):
    """Create a CalendarOS event from natural language."""

    text = request.text.strip()

    if not text:
        return {
            "success": False,
            "status": "empty",
            "message": "Please describe the event.",
        }

    result = create_event_from_text(
        text
    )

    response = {
        "success": result.success,
        "status": result.status,
        "message": result.message,
    }

    if result.parsed_event:
        response["event"] = {
            "title": result.parsed_event.get(
                "title"
            ),
            "all_day": result.parsed_event.get(
                "all_day",
                False,
            ),
        }

        if result.parsed_event.get(
            "all_day"
        ):
            response["event"]["start"] = str(
                result.parsed_event.get(
                    "start_date"
                )
            )

            response["event"]["end"] = str(
                result.parsed_event.get(
                    "end_date"
                )
            )

        else:
            start_time = (
                result.parsed_event.get(
                    "start_time"
                )
            )

            end_time = (
                result.parsed_event.get(
                    "end_time"
                )
            )

            response["event"]["start"] = (
                start_time.isoformat()
                if start_time
                else None
            )

            response["event"]["end"] = (
                end_time.isoformat()
                if end_time
                else None
            )

    if result.created_event:
        response["calendar_link"] = (
            result.created_event.get(
                "htmlLink"
            )
        )

    return response

@app.get("/money")
def money_page(
    request: Request,
):
    """Render MoneyOS."""

    return templates.TemplateResponse(
        request=request,
        name="money.html",
        context={
            "page_title": "Money",
        },
    )

@app.get("/api/tasks")
def tasks_list():
    """Return all open TasksOS tasks."""

    result = get_tasks()

    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "count": len(result.tasks),
        "tasks": result.tasks,
    }


@app.post("/api/tasks/create")
def tasks_create(
    request: TaskCreateRequest,
):
    """Create a task from natural language."""

    result = create_task_from_text(
        request.text
    )

    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "task": result.task,
    }


@app.post("/api/tasks/{task_id}/complete")
def tasks_complete(
    task_id: int,
):
    """Complete an existing TasksOS task."""

    result = complete_task_by_id(
        task_id
    )

    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "task": result.task,
    }

@app.get("/tasks")
def tasks_page(
    request: Request,
):
    """Render TasksOS."""

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "page_title": "Tasks",
        },
    )

@app.get("/us")
def us_page(
    request: Request,
):
    """Render the shared Shaun & Maria space."""

    return templates.TemplateResponse(
        request=request,
        name="us.html",
        context={
            "page_title": "Us",
        },
    )