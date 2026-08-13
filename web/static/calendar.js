let selectedDate = new Date();
let visibleMonth = new Date(
    selectedDate.getFullYear(),
    selectedDate.getMonth(),
    1
);

let currentView =
    localStorage.getItem(
        "calendar-view"
    ) || "month";

let monthEvents = [];


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


function sameCalendarDay(
    first,
    second
) {
    return (
        first.getFullYear() ===
            second.getFullYear()
        &&
        first.getMonth() ===
            second.getMonth()
        &&
        first.getDate() ===
            second.getDate()
    );
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
    const weekdayElement =
        document.getElementById(
            "calendar-weekday"
        );

    const titleElement =
        document.getElementById(
            "calendar-date-title"
        );

    if (
        !weekdayElement ||
        !titleElement
    ) {
        return;
    }

    weekdayElement.textContent =
        selectedDate
            .toLocaleDateString(
                "en-SG",
                {
                    weekday: "long",
                }
            )
            .toUpperCase();

    titleElement.textContent =
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


function updateAgendaHeading() {
    const weekdayElement =
        document.getElementById(
            "agenda-weekday"
        );

    const titleElement =
        document.getElementById(
            "agenda-date-title"
        );

    if (
        !weekdayElement ||
        !titleElement
    ) {
        return;
    }

    weekdayElement.textContent =
        selectedDate
            .toLocaleDateString(
                "en-SG",
                {
                    weekday: "long",
                }
            )
            .toUpperCase();

    titleElement.textContent =
        selectedDate
            .toLocaleDateString(
                "en-SG",
                {
                    day: "numeric",
                    month: "long",
                }
            );
}


function updateMonthHeading() {
    const titleElement =
        document.getElementById(
            "calendar-month-title"
        );

    if (!titleElement) {
        return;
    }

    titleElement.textContent =
        visibleMonth
            .toLocaleDateString(
                "en-SG",
                {
                    month: "long",
                    year: "numeric",
                }
            );
}


function buildCalendarEvent(event) {
    const card =
        document.createElement(
            "article"
        );

    card.className =
        "card schedule-card";

    const time = event.all_day
        ? "All day"
        : formatEventTime(
            event.start
        );

    const details = event.all_day
        ? "All-day event"
        : (
            `${formatEventTime(
                event.start
            )} – ${formatEventTime(
                event.end
            )}`
        );

    card.innerHTML = `
        <div class="schedule-time">
            ${time}
        </div>

        <div class="calendar-event-info">
            <strong>
                ${escapeHtml(event.title)}
            </strong>

            <p>
                ${escapeHtml(details)}
            </p>
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


function escapeHtml(value) {
    return String(
        value ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


function getEventDateRange(event) {
    if (event.all_day) {
        const start =
            new Date(
                `${event.start}T00:00:00+08:00`
            );

        /*
         * Google Calendar returns the all-day
         * end date as exclusive.
         */
        const exclusiveEnd =
            new Date(
                `${event.end}T00:00:00+08:00`
            );

        const end =
            new Date(
                exclusiveEnd
            );

        end.setDate(
            end.getDate() - 1
        );

        return {
            start,
            end,
        };
    }

    return {
        start: new Date(
            event.start
        ),
        end: new Date(
            event.end
        ),
    };
}


function eventOccursOnDate(
    event,
    date
) {
    const range =
        getEventDateRange(event);

    const target =
        new Date(
            date.getFullYear(),
            date.getMonth(),
            date.getDate()
        );

    const start =
        new Date(
            range.start.getFullYear(),
            range.start.getMonth(),
            range.start.getDate()
        );

    const end =
        new Date(
            range.end.getFullYear(),
            range.end.getMonth(),
            range.end.getDate()
        );

    return (
        target >= start &&
        target <= end
    );
}

function isMultiDayAllDayEvent(event) {
    if (!event.all_day) {
        return false;
    }

    const range =
        getEventDateRange(event);

    return !sameCalendarDay(
        range.start,
        range.end
    );
}


function getSingleDayEventsForDate(date) {
    return monthEvents.filter(
        event => {
            if (
                isMultiDayAllDayEvent(
                    event
                )
            ) {
                return false;
            }

            return eventOccursOnDate(
                event,
                date
            );
        }
    );
}


function getGridDateIndex(
    gridStart,
    date
) {
    const start =
        new Date(
            gridStart.getFullYear(),
            gridStart.getMonth(),
            gridStart.getDate()
        );

    const target =
        new Date(
            date.getFullYear(),
            date.getMonth(),
            date.getDate()
        );

    const millisecondsPerDay =
        24 * 60 * 60 * 1000;

    return Math.round(
        (
            target.getTime()
            - start.getTime()
        )
        / millisecondsPerDay
    );
}


function getEventsForSelectedDate() {
    return monthEvents.filter(
        event =>
            eventOccursOnDate(
                event,
                selectedDate
            )
    );
}


function renderAgendaEvents() {
    const container =
        document.getElementById(
            "month-day-events"
        );

    if (!container) {
        return;
    }

    updateAgendaHeading();

    container.innerHTML = "";

    const events =
        getEventsForSelectedDate();

    if (!events.length) {
        container.innerHTML = `
            <article
                class="card schedule-card empty-schedule"
            >
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

    events.forEach(
        event => {
            container.appendChild(
                buildCalendarEvent(
                    event
                )
            );
        }
    );
}


function buildMonthDayCell(
    date,
    isCurrentMonth
) {
    const button =
        document.createElement(
            "button"
        );

    button.type = "button";
    button.className =
        "calendar-month-day";

    const today =
        new Date();

    if (!isCurrentMonth) {
        button.classList.add(
            "outside-month"
        );
    }

    if (
        sameCalendarDay(
            date,
            today
        )
    ) {
        button.classList.add(
            "today"
        );
    }

    if (
        sameCalendarDay(
            date,
            selectedDate
        )
    ) {
        button.classList.add(
            "selected"
        );
    }

    const events =
        getSingleDayEventsForDate(
            date
        );

    const visibleEvents =
        events.slice(
            0,
            2
        );

    const remaining =
        events.length
        - visibleEvents.length;

    const eventMarkup =
        visibleEvents
            .map(
                event => `
                    <span
                        class="calendar-month-event"
                    >
                        ${escapeHtml(
                            event.title
                        )}
                    </span>
                `
            )
            .join("");

    const moreMarkup =
        remaining > 0
            ? `
                <span
                    class="calendar-month-more"
                >
                    +${remaining} more
                </span>
            `
            : "";

    button.innerHTML = `
        <span
            class="calendar-month-day-number"
        >
            ${date.getDate()}
        </span>

        <span
            class="calendar-month-day-events"
        >
            ${eventMarkup}
            ${moreMarkup}
        </span>
    `;

    button.addEventListener(
        "click",
        () => {
            selectedDate =
                new Date(date);

            /*
             * If an adjacent-month date is
             * tapped, move the visible month
             * to match it.
             */
            if (
                selectedDate.getMonth()
                    !==
                visibleMonth.getMonth()
                ||
                selectedDate.getFullYear()
                    !==
                visibleMonth.getFullYear()
            ) {
                visibleMonth =
                    new Date(
                        selectedDate
                            .getFullYear(),
                        selectedDate
                            .getMonth(),
                        1
                    );

                loadMonth();
                return;
            }

            renderMonthGrid();
            renderAgendaEvents();
        }
    );

    return button;
}

function renderMultiDayEvents(
    grid,
    gridStart
) {
    const multiDayEvents =
        monthEvents.filter(
            isMultiDayAllDayEvent
        );

    const firstCell =
        grid.querySelector(
            ".calendar-month-day"
        );

    if (!firstCell) {
        return;
    }

    const cellWidth =
        grid.clientWidth / 7;

    const cellHeight =
        firstCell.getBoundingClientRect()
            .height;


    multiDayEvents.forEach(
        event => {
            const range =
                getEventDateRange(
                    event
                );

            let eventStart =
                new Date(range.start);

            let eventEnd =
                new Date(range.end);

            const gridEnd =
                new Date(gridStart);

            gridEnd.setDate(
                gridStart.getDate() + 41
            );

            if (
                eventEnd < gridStart ||
                eventStart > gridEnd
            ) {
                return;
            }

            if (eventStart < gridStart) {
                eventStart =
                    new Date(gridStart);
            }

            if (eventEnd > gridEnd) {
                eventEnd =
                    new Date(gridEnd);
            }

            let segmentStart =
                new Date(eventStart);

            while (
                segmentStart <= eventEnd
            ) {
                const startIndex =
                    getGridDateIndex(
                        gridStart,
                        segmentStart
                    );

                const columnIndex =
                    startIndex % 7;

                const rowIndex =
                    Math.floor(
                        startIndex / 7
                    );

                const remainingDaysInWeek =
                    7 - columnIndex;

                const remainingEventDays =
                    getGridDateIndex(
                        segmentStart,
                        eventEnd
                    ) + 1;

                const segmentLength =
                    Math.min(
                        remainingDaysInWeek,
                        remainingEventDays
                    );

                const bar =
                    document.createElement(
                        "button"
                    );

                bar.type = "button";

                bar.className =
                    "calendar-multi-day-event";

                bar.style.left =
                    `${columnIndex * cellWidth}px`;

                const barHeight = 19;
                const bottomGap = 5;

                bar.style.top =
                    `${
                        (
                            rowIndex + 1
                        ) * cellHeight
                        - barHeight
                        - bottomGap
                    }px`;

                bar.style.width =
                    `${
                        segmentLength
                        * cellWidth
                    }px`;

                const isFirstSegment =
                    sameCalendarDay(
                        segmentStart,
                        range.start
                    );

                bar.textContent =
                    isFirstSegment
                        ? event.title
                        : "";

                bar.title =
                    event.title;

                const selectedSegmentDate =
                    new Date(
                        segmentStart
                    );

                bar.addEventListener(
                    "click",
                    clickEvent => {
                        clickEvent
                            .stopPropagation();

                        selectedDate =
                            new Date(
                                selectedSegmentDate
                            );

                        renderMonthGrid();
                        renderAgendaEvents();
                    }
                );

                grid.appendChild(
                    bar
                );

                segmentStart.setDate(
                    segmentStart.getDate()
                    + segmentLength
                );
            }
        }
    );
}
function renderMonthGrid() {
    const grid =
        document.getElementById(
            "calendar-month-grid"
        );

    if (!grid) {
        return;
    }

    grid.innerHTML = "";

    const year =
        visibleMonth.getFullYear();

    const month =
        visibleMonth.getMonth();

    const firstOfMonth =
        new Date(
            year,
            month,
            1
        );

    const startOffset =
        (
            firstOfMonth.getDay()
            + 6
        ) % 7;

    const gridStart =
        new Date(
            year,
            month,
            1 - startOffset
        );

    for (
        let index = 0;
        index < 42;
        index += 1
    ) {
        const date =
            new Date(
                gridStart
            );

        date.setDate(
            gridStart.getDate()
            + index
        );

        const isCurrentMonth =
            date.getMonth()
            === month;

        grid.appendChild(
            buildMonthDayCell(
                date,
                isCurrentMonth
            )
        );
    }

    renderMultiDayEvents(
        grid,
        gridStart
    );
}


async function loadMonth() {
    updateMonthHeading();

    const grid =
        document.getElementById(
            "calendar-month-grid"
        );

    if (grid) {
        grid.innerHTML = `
            <div
                class="calendar-month-loading"
            >
                Loading calendar…
            </div>
        `;
    }

    const year =
        visibleMonth.getFullYear();

    const month =
        visibleMonth.getMonth()
        + 1;

    try {
        const response =
            await fetch(
                `/api/calendar/month/${year}/${month}`
            );

        const data =
            await response.json();

        if (!data.success) {
            if (grid) {
                grid.innerHTML = `
                    <div
                        class="calendar-month-loading"
                    >
                        Calendar unavailable.
                    </div>
                `;
            }

            return;
        }

        monthEvents =
            data.events || [];

        renderMonthGrid();
        renderAgendaEvents();

    } catch (error) {
        console.error(
            "Calendar month failed:",
            error
        );

        if (grid) {
            grid.innerHTML = `
                <div
                    class="calendar-month-loading"
                >
                    Calendar unavailable.
                </div>
            `;
        }
    }
}


async function loadSelectedDate() {
    const container =
        document.getElementById(
            "calendar-events"
        );

    if (!container) {
        return;
    }

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
        const response =
            await fetch(
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
                <article
                    class="card schedule-card empty-schedule"
                >
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
                    buildCalendarEvent(
                        event
                    )
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


function changeMonth(amount) {
    visibleMonth =
        new Date(
            visibleMonth.getFullYear(),
            visibleMonth.getMonth()
                + amount,
            1
        );

    selectedDate =
        new Date(
            visibleMonth.getFullYear(),
            visibleMonth.getMonth(),
            1
        );

    loadMonth();
}


function setCalendarView(view) {
    currentView = view;

    localStorage.setItem(
        "calendar-view",
        view
    );

    const monthView =
        document.getElementById(
            "month-view"
        );

    const dayView =
        document.getElementById(
            "day-view"
        );

    const monthButton =
        document.getElementById(
            "month-view-button"
        );

    const dayButton =
        document.getElementById(
            "day-view-button"
        );

    const showMonth =
        view === "month";

    monthView.classList.toggle(
        "calendar-view-hidden",
        !showMonth
    );

    dayView.classList.toggle(
        "calendar-view-hidden",
        showMonth
    );

    monthButton.classList.toggle(
        "active",
        showMonth
    );

    dayButton.classList.toggle(
        "active",
        !showMonth
    );

    monthButton.setAttribute(
        "aria-pressed",
        String(showMonth)
    );

    dayButton.setAttribute(
        "aria-pressed",
        String(!showMonth)
    );

    if (showMonth) {
        visibleMonth =
            new Date(
                selectedDate.getFullYear(),
                selectedDate.getMonth(),
                1
            );

        loadMonth();
    } else {
        updateDateHeading();
        loadSelectedDate();
    }
}


function formatCreatedEvent(event) {
    if (!event) {
        return "";
    }

    if (event.all_day) {
        return event.title;
    }

    const start =
        formatEventTime(
            event.start
        );

    return (
        `${event.title} · ${start}`
    );
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

    const text =
        input.value.trim();

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
        const response =
            await fetch(
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
                    ${escapeHtml(
                        data.message
                    )}
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
                    ${escapeHtml(
                        eventLabel
                    )}
                </span>

                ${link}
            </div>
        `;

        input.value = "";

        if (
            data.event &&
            data.event.start
        ) {
            const eventDate =
                new Date(
                    data.event.all_day
                        ? (
                            `${data.event.start}`
                            + "T00:00:00+08:00"
                        )
                        : data.event.start
                );

            if (
                !Number.isNaN(
                    eventDate.getTime()
                )
            ) {
                selectedDate =
                    eventDate;

                visibleMonth =
                    new Date(
                        eventDate.getFullYear(),
                        eventDate.getMonth(),
                        1
                    );
            }
        }

        if (
            currentView === "month"
        ) {
            loadMonth();
        } else {
            updateDateHeading();
            loadSelectedDate();
        }

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
    selectedDate =
        new Date();

    visibleMonth =
        new Date(
            selectedDate.getFullYear(),
            selectedDate.getMonth(),
            1
        );

    if (
        currentView === "month"
    ) {
        loadMonth();
    } else {
        updateDateHeading();
        loadSelectedDate();
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {
        document.getElementById(
            "month-view-button"
        ).addEventListener(
            "click",
            () => {
                setCalendarView(
                    "month"
                );
            }
        );

        document.getElementById(
            "day-view-button"
        ).addEventListener(
            "click",
            () => {
                setCalendarView(
                    "day"
                );
            }
        );

        document.getElementById(
            "previous-month"
        ).addEventListener(
            "click",
            () => {
                changeMonth(-1);
            }
        );

        document.getElementById(
            "next-month"
        ).addEventListener(
            "click",
            () => {
                changeMonth(1);
            }
        );

        document.getElementById(
            "previous-day"
        ).addEventListener(
            "click",
            () => {
                changeDay(-1);
            }
        );

        document.getElementById(
            "next-day"
        ).addEventListener(
            "click",
            () => {
                changeDay(1);
            }
        );

        document.getElementById(
            "today-button"
        ).addEventListener(
            "click",
            goToToday
        );

        document.getElementById(
            "month-today-button"
        ).addEventListener(
            "click",
            goToToday
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
                if (
                    event.key === "Enter"
                ) {
                    createQuickEvent();
                }
            }
        );

        setCalendarView(
            currentView
        );
    }
);