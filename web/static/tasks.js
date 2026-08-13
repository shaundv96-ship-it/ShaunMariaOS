function escapeHtml(value) {
    const element =
        document.createElement("div");

    element.textContent =
        value ?? "";

    return element.innerHTML;
}

function getTaskOwner() {
    return localStorage.getItem(
        "shaunmaria-owner"
    );
}


function chooseTaskOwner() {
    const existingOwner =
        getTaskOwner();

    if (existingOwner) {
        return existingOwner;
    }

    const answer =
        window.prompt(
            "Who is using ShaunMariaOS on this device? Type Shaun or Maria."
        );

    if (!answer) {
        return null;
    }

    const normalized =
        answer.trim().toLowerCase();

    let owner = null;

    if (normalized === "shaun") {
        owner = "Shaun";
    }

    if (normalized === "maria") {
        owner = "Maria";
    }

    if (!owner) {
        window.alert(
            "Please enter Shaun or Maria."
        );

        return null;
    }

    localStorage.setItem(
        "shaunmaria-owner",
        owner
    );

    return owner;
}

function buildTaskCard(task) {
    const article =
        document.createElement(
            "article"
        );

    article.className =
        "card task-card";

    const owner =
        task.owner || "Anyone";

    const priority =
        task.priority || "Medium";

    article.innerHTML = `
        <button
            class="task-complete-button"
            type="button"
            aria-label="Complete task"
        >
            ✓
        </button>

        <div class="task-info">

    <div class="task-title-row">

        <strong>
            ${escapeHtml(task.task)}
        </strong>

        <button
            class="task-edit-button"
            type="button"
        >
            Edit
        </button>

    </div>

    <div class="task-meta">
        <span>
            ${escapeHtml(task.category)}
        </span>

        <span>
            ${escapeHtml(owner)}
        </span>

        <span>
            ${escapeHtml(priority)}
        </span>
    </div>

    ${
        task.due_date
        ? `
            <small>
                Due ${escapeHtml(task.due_date)}
            </small>
        `
        : ""
    }

</div>

        

        </div>
    `;

    article
        .querySelector(
            ".task-complete-button"
        )
        .addEventListener(
            "click",
            () => completeTask(task.id)
        );


    article
    .querySelector(
        ".task-edit-button"
    )
    .addEventListener(
        "click",
        () => openTaskEditor(task)
    );

    return article;
}

let editingTaskId = null;


function taskDateToInputValue(
    dueDate
) {
    if (!dueDate) {
        return "";
    }

    const parsed =
        new Date(dueDate);

    if (
        Number.isNaN(
            parsed.getTime()
        )
    ) {
        return "";
    }

    const year =
        parsed.getFullYear();

    const month =
        String(
            parsed.getMonth() + 1
        ).padStart(2, "0");

    const day =
        String(
            parsed.getDate()
        ).padStart(2, "0");

    return `${year}-${month}-${day}`;
}


function inputDateToTaskDate(
    value
) {
    if (!value) {
        return "";
    }

    const [
        year,
        month,
        day,
    ] = value
        .split("-")
        .map(Number);

    const date =
        new Date(
            year,
            month - 1,
            day
        );

    return (
        `${date.getDate()} `
        + date.toLocaleDateString(
            "en-SG",
            {
                month: "long",
                year: "numeric",
            }
        )
    );
}


function openTaskEditor(task) {
    editingTaskId =
        task.id;

    document.getElementById(
        "task-edit-name"
    ).value =
        task.task || "";

    document.getElementById(
        "task-edit-owner"
    ).value =
        task.owner || "";

    document.getElementById(
        "task-edit-priority"
    ).value =
        task.priority || "Medium";

    document.getElementById(
        "task-edit-due-date"
    ).value =
        taskDateToInputValue(
            task.due_date
        );

    document.getElementById(
        "task-edit-result"
    ).innerHTML = "";

    const editor =
        document.getElementById(
            "task-editor"
        );

    editor.hidden = false;

    editor.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


function closeTaskEditor() {
    editingTaskId = null;

    document.getElementById(
        "task-editor"
    ).hidden = true;
}

async function loadTasks() {
    const list =
        document.getElementById(
            "task-list"
        );

    try {
        const response =
            await fetch(
                "/api/tasks"
            );

        const data =
            await response.json();

        document.getElementById(
            "task-count"
        ).textContent =
            data.count ?? 0;

        list.innerHTML = "";

        if (!data.success) {
            list.innerHTML = `
                <article class="card">
                    TasksOS is unavailable.
                </article>
            `;
            return;
        }

        if (!data.tasks.length) {
            list.innerHTML = `
                <article class="card empty-schedule">
                    <div class="schedule-card">
                        <div class="schedule-time">
                            ✨
                        </div>

                        <div>
                            <strong>
                                All caught up
                            </strong>

                            <p>
                                Nothing waiting for you.
                            </p>
                        </div>
                    </div>
                </article>
            `;
            return;
        }

        data.tasks.forEach(
            task => {
                list.appendChild(
                    buildTaskCard(task)
                );
            }
        );

    } catch (error) {
        console.error(
            "TasksOS failed:",
            error
        );
    }
}


async function createTask() {
    const input =
        document.getElementById(
            "task-input"
        );

    const owner =
    chooseTaskOwner();

    if (!owner) {
    return;
}

    const result =
        document.getElementById(
            "task-result"
        );

    const text =
        input.value.trim();

    if (!text) {
        return;
    }

    try {
        const response =
            await fetch(
                "/api/tasks/create",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        text: text,
                        owner: owner,
                    }),
                }
            );

        const data =
            await response.json();

        if (!data.success) {
            result.innerHTML = `
                <p class="quick-add-error">
                    ${escapeHtml(data.message)}
                </p>
            `;
            return;
        }

        input.value = "";

        result.innerHTML = `
            <div class="quick-add-success">
                <strong>
                    ✓ Task added
                </strong>

                <span>
                    ${escapeHtml(data.task.task)}
                </span>
            </div>
        `;

        await loadTasks();

    } catch (error) {
        console.error(
            "Task creation failed:",
            error
        );
    }
}

async function saveTaskEdit() {
    if (editingTaskId === null) {
        return;
    }

    const taskName =
        document.getElementById(
            "task-edit-name"
        ).value.trim();

    const owner =
        document.getElementById(
            "task-edit-owner"
        ).value;

    const priority =
        document.getElementById(
            "task-edit-priority"
        ).value;

    const dueDateInput =
        document.getElementById(
            "task-edit-due-date"
        ).value;

    const result =
        document.getElementById(
            "task-edit-result"
        );

    if (!taskName) {
        result.innerHTML = `
            <p class="quick-add-error">
                Task name cannot be empty.
            </p>
        `;

        return;
    }

    try {
        const response =
            await fetch(
                `/api/tasks/${editingTaskId}/update`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        task: taskName,
                        owner: owner,
                        priority: priority,
                        due_date:
                            inputDateToTaskDate(
                                dueDateInput
                            ),
                    }),
                }
            );

        const data =
            await response.json();

        if (!data.success) {
            result.innerHTML = `
                <p class="quick-add-error">
                    ${escapeHtml(
                        data.message
                    )}
                </p>
            `;

            return;
        }

        result.innerHTML = `
            <div class="quick-add-success">
                <strong>
                    ✓ Task updated
                </strong>
            </div>
        `;

        await loadTasks();

        setTimeout(
            closeTaskEditor,
            500
        );

    } catch (error) {
        console.error(
            "Task update failed:",
            error
        );

        result.innerHTML = `
            <p class="quick-add-error">
                Something went wrong.
            </p>
        `;
    }
}

async function completeTask(taskId) {
    try {
        const response =
            await fetch(
                `/api/tasks/${taskId}/complete`,
                {
                    method: "POST",
                }
            );

        const data =
            await response.json();

        if (data.success) {
            await loadTasks();
        }

    } catch (error) {
        console.error(
            "Task completion failed:",
            error
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadTasks();

        document.getElementById(
            "task-add-button"
        ).addEventListener(
            "click",
            createTask
        );

        document.getElementById(
            "task-input"
        ).addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    createTask();
                }
            }
        );

        document.getElementById(
    "task-editor-close"
).addEventListener(
    "click",
    closeTaskEditor
);

document.getElementById(
    "task-edit-cancel"
).addEventListener(
    "click",
    closeTaskEditor
);

document.getElementById(
    "task-edit-save"
).addEventListener(
    "click",
    saveTaskEdit
);
    }
);