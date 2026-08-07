function escapeHtml(value) {
    const element =
        document.createElement("div");

    element.textContent =
        value ?? "";

    return element.innerHTML;
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

            <strong>
                ${escapeHtml(task.task)}
            </strong>

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
    `;

    article
        .querySelector(
            ".task-complete-button"
        )
        .addEventListener(
            "click",
            () => completeTask(task.id)
        );

    return article;
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
    }
);