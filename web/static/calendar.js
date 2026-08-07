let selectedDate = new Date();


function toLocalISODate(date) {
    const year = date.getFullYear();

    const month = String(
        date.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        date.getDate()
    ).padStart(2, "0");

    return `${year}-${month}-${day}`;
}


function formatEventTime(value) {
    if (!value) {
        return "All day";
    }

    const date = new Date(value);

    return date.toLocaleTimeString(
        "en-SG",
        {
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
        }
    );
}


function updateDateHeading() {
    document.getElementById(
        "calendar-weekday"
    ).textContent =
        selectedDate
            .toLocaleDateString(
                "en-SG",
                {
                    weekday: "long",
                }
            )
            .toUpperCase();

    document.getElementById(
        "calendar-date-title"
    ).textContent =
        selectedDate
            .toLocaleDateString(
                "en-SG",
                {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                }
            );
}


function buildCalendarEvent(event) {
    const card = document.createElement(
        "article"
    );

    card.className =
        "card schedule-card";

    const time = event.all_day
        ? "All day"
        : formatEventTime(event.start);

    const details = event.all_day
        ? "All-day event"
        : `${formatEventTime(event.start)} – ${formatEventTime(event.end)}`;

    card.innerHTML = `
        <div class="schedule-time">
            ${time}
        </div>

        <div class="calendar-event-info">
            <strong>${event.title}</strong>
            <p>${details}</p>
        </div>
    `;

    if (event.calendar_link) {
        card.addEventListener(
            "click",
            () => {
                window.open(
                    event.calendar_link,
                    "_blank"
                );
            }
        );

        card.classList.add(
            "clickable-card"
        );
    }

    return card;
}


async function loadSelectedDate() {
    const container =
        document.getElementById(
            "calendar-events"
        );

    container.innerHTML = `
        <article class="card schedule-card">
            <div>
                <strong>
                    Loading…
                </strong>
            </div>
        </article>
    `;

    const dateText =
        toLocalISODate(
            selectedDate
        );

    try {
        const response = await fetch(
            `/api/calendar/date/${dateText}`
        );

        const data =
            await response.json();

        container.innerHTML = "";

        if (!data.success) {
            container.innerHTML = `
                <article class="card schedule-card">
                    <div>
                        <strong>
                            Calendar unavailable
                        </strong>

                        <p>
                            Please try again.
                        </p>
                    </div>
                </article>
            `;

            return;
        }

        if (!data.events.length) {
            container.innerHTML = `
                <article class="card schedule-card empty-schedule">
                    <div class="schedule-time">
                        ✨
                    </div>

                    <div>
                        <strong>
                            Nothing planned
                        </strong>

                        <p>
                            This day is clear.
                        </p>
                    </div>
                </article>
            `;

            return;
        }

        data.events.forEach(
            event => {
                container.appendChild(
                    buildCalendarEvent(event)
                );
            }
        );

    } catch (error) {
        console.error(
            "CalendarOS failed:",
            error
        );
    }
}


function changeDay(amount) {
    selectedDate.setDate(
        selectedDate.getDate()
        + amount
    );

    updateDateHeading();
    loadSelectedDate();
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        updateDateHeading();
        loadSelectedDate();

        document.getElementById(
            "previous-day"
        ).addEventListener(
            "click",
            () => changeDay(-1)
        );

        document.getElementById(
            "next-day"
        ).addEventListener(
            "click",
            () => changeDay(1)
        );

        document.getElementById(
            "quick-add-button"
        ).addEventListener(
            "click",
            createQuickEvent
        );


        document.getElementById(
            "quick-add-input"
        ).addEventListener(
            "keydown",
            event => {
            if (event.key === "Enter") {
                createQuickEvent();
            }
        }
        );

        document.getElementById(
            "today-button"
        ).addEventListener(
            "click",
        goToToday
        );
    }
);

function formatCreatedEvent(event) {
    if (!event) {
        return "";
    }

    if (event.all_day) {
        return event.title;
    }

    const start =
        formatEventTime(event.start);

    return `${event.title} · ${start}`;
}


async function createQuickEvent() {
    const input =
        document.getElementById(
            "quick-add-input"
        );

    const button =
        document.getElementById(
            "quick-add-button"
        );

    const resultBox =
        document.getElementById(
            "quick-add-result"
        );

    const text = input.value.trim();

    if (!text) {
        resultBox.innerHTML = `
            <p class="quick-add-error">
                Tell me what you'd like to add.
            </p>
        `;

        input.focus();
        return;
    }

    button.disabled = true;
    input.disabled = true;

    button.textContent = "…";

    resultBox.innerHTML = `
        <p class="quick-add-loading">
            Adding to your calendar…
        </p>
    `;

    try {
        const response = await fetch(
            "/api/calendar/create",
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
            resultBox.innerHTML = `
                <p class="quick-add-error">
                    ${data.message}
                </p>
            `;

            return;
        }

        const eventLabel =
            formatCreatedEvent(
                data.event
            );

        let link = "";

        if (data.calendar_link) {
            link = `
                <a
                    href="${data.calendar_link}"
                    target="_blank"
                    rel="noopener"
                >
                    View event →
                </a>
            `;
        }

        resultBox.innerHTML = `
            <div class="quick-add-success">
                <strong>
                    ✓ Added
                </strong>

                <span>
                    ${eventLabel}
                </span>

                ${link}
            </div>
        `;

        input.value = "";
            if (
    data.event
    && data.event.start
) {
    const eventDate =
        new Date(
            data.event.start
        );

    if (!Number.isNaN(
        eventDate.getTime()
    )) {
        selectedDate =
            eventDate;

        updateDateHeading();
    }
}
        /*
         * Reload the visible day in case the
         * newly-created event belongs to it.
         */
        loadSelectedDate();

    } catch (error) {
        console.error(
            "Quick Add failed:",
            error
        );

        resultBox.innerHTML = `
            <p class="quick-add-error">
                Something went wrong.
                Please try again.
            </p>
        `;

    } finally {
        button.disabled = false;
        input.disabled = false;

        button.textContent = "+";
        input.focus();
    }
}

function goToToday() {
    selectedDate = new Date();

    updateDateHeading();
    loadSelectedDate();
}