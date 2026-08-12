"""
ShaunMariaOS

Task Engine
"""

from dataclasses import dataclass
import re

from apps.database_engine import (
    TASKS_SHEET,
    get_tasks_sheet,
)
from apps.task_category_rules import (
    DEFAULT_TASK_CATEGORY,
    detect_task_category,
)
from services.sheet_writer import (
    append_row,
    update_cells,
)
from utils.time import sg_now
from apps.calendar_parser import (
    normalize_calendar_text,
    parse_calendar_date,
)

@dataclass
class TaskEntry:
    task: str
    category: str = DEFAULT_TASK_CATEGORY
    owner: str = ""
    priority: str = "Medium"
    due_date: str = ""


def extract_task_due_date(
    text: str,
) -> tuple[str, str]:
    """
    Extract a due date from natural-language task text.

    Examples:
        Pay JB accommodation on Oct 5
        Submit documents by 30 Sept
        Renew insurance due 1 October
    """

    normalized = normalize_calendar_text(
        text
    )

    due_pattern = re.compile(
        r"\b(?:on|by|due(?:\s+on)?)\s+"
        r"("
        r"(?:"
        r"january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december"
        r")\s+\d{1,2}(?:\s+\d{4})?"
        r"|"
        r"\d{1,2}\s+(?:"
        r"january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december"
        r")(?:\s+\d{4})?"
        r"|today"
        r"|tomorrow"
        r")\b",
        re.IGNORECASE,
    )

    match = due_pattern.search(
        normalized
    )

    if not match:
        return (
            text.strip(),
            "",
        )

    due_text = match.group(1)

    due_date = parse_calendar_date(
        due_text
    )

    if due_date is None:
        return (
            text.strip(),
            "",
        )

    cleaned_task = (
        normalized[:match.start()]
        + " "
        + normalized[match.end():]
    )

    cleaned_task = re.sub(
        r"\s+",
        " ",
        cleaned_task,
    ).strip(" ,.-")

    formatted_due_date = (
        due_date.strftime(
            "%d %B %Y"
        ).lstrip("0")
    )

    return (
        cleaned_task,
        formatted_due_date,
    )
def restore_task_acronyms(
    text: str,
) -> str:
    """Restore common acronyms after task parsing."""

    acronyms = {
        "jb": "JB",
        "bto": "BTO",
        "cpf": "CPF",
        "hdb": "HDB",
        "sg": "SG",
        "kl": "KL",
        "hr": "HR",
    }

    for word, replacement in acronyms.items():
        text = re.sub(
            rf"\b{re.escape(word)}\b",
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    return text
def parse_task(
    text: str,
) -> TaskEntry | None:
    """
    Extract and categorise a new task
    from natural language.
    """

    task_text = text.strip()

    prefixes = (
        "remember to ",
        "remind me to ",
        "need to ",
        "add ",
        "todo ",
        "to do ",
        "task ",
    )

    lowered = task_text.casefold()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            task_text = (
                task_text[
                    len(prefix):
                ].strip()
            )
            break

    if not task_text:
        return None

    task_text, due_date = (
        extract_task_due_date(
            task_text
        )
    )

    task_text = restore_task_acronyms(
    task_text
    )
    
    if not task_text:
        return None

    task_text = (
        task_text[0].upper()
        + task_text[1:]
    )

    return TaskEntry(
        task=task_text,
        category=detect_task_category(
            task_text
        ),
        due_date=due_date,
    )

def parse_task_completion(text: str) -> int | None:
    """
    Extract the task ID from completion messages.

    Examples:
        Done 1
        Complete 3
        Completed #5
    """

    match = re.fullmatch(
        r"(?:done|complete|completed)\s+#?(\d+)",
        text.strip(),
        re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))


def get_next_task_id() -> int:
    """Return the next available numeric task ID."""

    rows = get_tasks_sheet(
    force_refresh=True,
    )
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
    """Append a new task to the Tasks worksheet."""

    date_text = sg_now().strftime("%d %B %Y")
    task_id = get_next_task_id()

    values = [
        task_id,
        entry.task,
        entry.owner,
        entry.priority,
        entry.due_date,
        date_text,
        "",
        "Open",
        date_text,
        entry.category,
    ]

    append_row(
        TASKS_SHEET,
        values,
    )

    get_tasks_sheet(
    force_refresh=True,
    )

    return {
        "id": task_id,
        "task": entry.task,
        "category": entry.category,
        "owner": entry.owner,
        "priority": entry.priority,
        "due_date": entry.due_date,
    }


def get_open_tasks() -> list[dict]:
    """Return all tasks whose status is Open."""

    rows = get_tasks_sheet()
    tasks = []

    for row in rows:
        if len(row) < 8:
            continue

        try:
            task_id = int(str(row[0]).strip())
        except (ValueError, TypeError):
            continue

        status = str(row[7]).strip().casefold()

        if status != "open":
            continue

        task_text = (
            str(row[1]).strip()
            if len(row) > 1
            else ""
        )

        category = (
            str(row[9]).strip()
            if len(row) > 9 and str(row[9]).strip()
            else detect_task_category(task_text)
        )

        tasks.append(
            {
                "id": task_id,
                "task": task_text,
                "category": category,
                "owner": (
                    str(row[2]).strip()
                    if len(row) > 2
                    else ""
                ),
                "priority": (
                    str(row[3]).strip()
                    if len(row) > 3
                    else "Medium"
                ),
                "due_date": (
                    str(row[4]).strip()
                    if len(row) > 4
                    else ""
                ),
            }
        )
    

    return tasks


def complete_task(task_id: int) -> dict:
    """Mark a task as completed using its ID."""

    rows = get_tasks_sheet(
        force_refresh=True,
    )
    target_row = None
    task_name = ""

    for row_number, row in enumerate(
        rows,
        start=1,
    ):
        if not row:
            continue

        try:
            row_task_id = int(str(row[0]).strip())
        except (ValueError, TypeError, IndexError):
            continue

        if row_task_id == task_id:
            target_row = row_number
            task_name = (
                str(row[1]).strip()
                if len(row) > 1
                else ""
            )
            break

    if target_row is None:
        raise ValueError(
            f"Task {task_id} could not be found."
        )

    date_text = sg_now().strftime("%d %B %Y")

    update_cells(
        TASKS_SHEET,
        {
            f"G{target_row}": date_text,
            f"H{target_row}": "Completed",
            f"I{target_row}": date_text,
        },
    )

    return {
        "id": task_id,
        "task": task_name,
    }