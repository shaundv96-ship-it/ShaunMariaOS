"""
ShaunMariaOS

Task Service
Shared task business logic used by Telegram and the web app.
"""

from dataclasses import dataclass

from apps.task_engine import (
    complete_task,
    get_open_tasks,
    parse_task,
    save_task,
    update_task,
)


@dataclass
class TaskListResult:
    """Result returned when loading open tasks."""

    success: bool
    status: str
    message: str
    tasks: list[dict]


@dataclass
class TaskActionResult:
    """Result returned when creating or completing a task."""

    success: bool
    status: str
    message: str
    task: dict | None = None


def get_tasks() -> TaskListResult:
    """Return all currently open tasks."""

    try:
        tasks = get_open_tasks()

        return TaskListResult(
            success=True,
            status="ok",
            message="Open tasks loaded.",
            tasks=tasks,
        )

    except Exception as exc:
        return TaskListResult(
            success=False,
            status="error",
            message=str(exc),
            tasks=[],
        )


def create_task_from_text(
    text: str,
    owner: str | None = None,
) -> TaskActionResult:
    """Create a task from natural-language text."""

    text = text.strip()

    if not text:
        return TaskActionResult(
            success=False,
            status="invalid",
            message="Tell me what you'd like to add.",
        )

    try:
        entry = parse_task(text)

        if entry is None:
            return TaskActionResult(
                success=False,
                status="invalid",
                message="I couldn't understand that task.",
            )

        if owner:
            entry.owner = owner

        task = save_task(entry)

        return TaskActionResult(
            success=True,
            status="created",
            message="Task added.",
            task=task,
        )

    except Exception as exc:
        return TaskActionResult(
            success=False,
            status="error",
            message=str(exc),
        )

def complete_task_by_id(task_id: int) -> TaskActionResult:
    """Complete an existing task."""

    try:
        task = complete_task(task_id)

        return TaskActionResult(
            success=True,
            status="completed",
            message="Task completed.",
            task=task,
        )

    except ValueError as exc:
        return TaskActionResult(
            success=False,
            status="not_found",
            message=str(exc),
        )

    except Exception as exc:
        return TaskActionResult(
            success=False,
            status="error",
            message=str(exc),
        )

def update_task_by_id(
    task_id: int,
    *,
    task_text: str,
    owner: str,
    priority: str,
    due_date: str,
) -> TaskActionResult:
    """Update an existing task."""

    try:
        task = update_task(
            task_id,
            task_text=task_text,
            owner=owner,
            priority=priority,
            due_date=due_date,
        )

        return TaskActionResult(
            success=True,
            status="updated",
            message="Task updated.",
            task=task,
        )

    except ValueError as exc:
        return TaskActionResult(
            success=False,
            status="invalid",
            message=str(exc),
        )

    except Exception as exc:
        return TaskActionResult(
            success=False,
            status="error",
            message=str(exc),
        )