"""
ShaunMariaOS

Command Service
Routes natural-language commands to the correct Core service.
"""

from dataclasses import dataclass
from typing import Any

from apps.intent_engine import detect_intent
from core.calendar_service import create_event_from_text
from core.task_service import create_task_from_text
from core.money_action_service import (
    record_expense_from_text,
    record_income_from_text,
)


@dataclass
class CommandResult:
    """Structured result returned by the global command router."""

    success: bool
    status: str
    message: str
    intent: str
    data: dict[str, Any] | None = None


def run_command(
    text: str,
) -> CommandResult:
    """
    Route natural-language input to the correct ShaunMariaOS service.

    Calendar, Tasks, Expenses and Income are supported.
    
    """

    text = text.strip()

    if not text:
        return CommandResult(
            success=False,
            status="empty",
            message="Tell me what you'd like to do.",
            intent="unknown",
        )

    intent = detect_intent(text)

    if intent.name == "calendar":
        result = create_event_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="calendar",
            data={
                "parsed_event": result.parsed_event,
                "created_event": result.created_event,
            },
        )

    if intent.name == "task":
        result = create_task_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="task",
            data={
                "task": result.task,
            },
        )

    if intent.name == "expense":
        result = record_expense_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="expense",
            data=result.data,
        )

    if intent.name == "income":
        result = record_income_from_text(
            text
        )

        return CommandResult(
            success=result.success,
            status=result.status,
            message=result.message,
            intent="income",
            data=result.data,
        ) 

    return CommandResult(
        success=False,
        status="unsupported",
        message=(
            "I understood the request, but this action "
            "isn't connected to the app yet."
        ),
        intent=intent.name,
    )