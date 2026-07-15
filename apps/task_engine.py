"""
ShaunMariaOS

Task Engine
"""

from dataclasses import dataclass

from apps.database_engine import (
    TASKS_SHEET,
    get_tasks_sheet,
)
from services.sheet_writer import append_row
from utils.time import sg_now


@dataclass
class TaskEntry:
    task: str
    owner: str = ""
    priority: str = "Medium"
    due_date: str = ""


def parse_task(text: str) -> TaskEntry | None:
    """Extract a task from a natural-language message."""

    task_text = text.strip()

    prefixes = [
        "remember to ",
        "remind me to ",
        "need to ",
        "todo ",
        "to do ",
        "task ",
    ]

    lowered = task_text.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            task_text = task_text[len(prefix):].strip()
            break

    if not task_text:
        return None

    task_text = task_text[0].upper() + task_text[1:]

    return TaskEntry(
        task=task_text,
    )


def get_next_task_id() -> int:
    """Return the next available numeric task ID."""

    rows = get_tasks_sheet()
    highest_id = 0

    for row in rows:
        if not row:
            continue

        try:
            task_id = int(str(row[0]).strip())
        except (ValueError, TypeError, IndexError):
            continue

        highest_id = max(highest_id, task_id)

    return highest_id + 1


def save_task(entry: TaskEntry) -> dict:
    """Append a task to the Tasks worksheet."""

    now = sg_now()
    date_text = now.strftime("%d %B %Y")

    values = [
        get_next_task_id(),
        entry.task,
        entry.owner,
        entry.priority,
        entry.due_date,
        date_text,
        "",
        "Open",
        date_text,
    ]

    return append_row(
        TASKS_SHEET,
        values,
    )