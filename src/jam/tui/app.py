"""JAM TUI proof of concept: search, add, edit and delete applications.

Talks to the FastAPI backend's /applications endpoints only. Everything lives in
this one file on purpose, so it's easy to split up once you know where you want
to take it.

Environment variables (a .env file is loaded too):
    JAM_API_URL     backend URL            (default http://localhost:8000)
    JAM_STUDENT_ID  student to act as      (default 1)
"""

import os
from collections.abc import Awaitable, Callable
from datetime import date
from typing import Any

import httpx
from dotenv import load_dotenv
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

Row = dict[str, Any]

# Must not exceed the backend's maximum `limit` (it currently rejects anything over 100).
PAGE_SIZE = 100

STATUSES = [
    "Not Applied",
    "Applied",
    "Interviewing",
    "Offer",
    "Accepted",
    "Declined",
    "Rejected",
    "Withdrawn",
    "Ghosted", # added just to show that the database rules enforce one of the allowed options.
]


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------


class ApiError(Exception):
    """Raised for any non-2xx response. status_code 0 means the server was unreachable."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


def _error_message(resp: httpx.Response) -> str:
    """Turn the backend's error body into one readable line."""
    try:
        body = resp.json()
    except ValueError:
        return resp.text or resp.reason_phrase
    if not isinstance(body, dict):
        return resp.reason_phrase
    detail = body.get("detail", resp.reason_phrase)
    if isinstance(detail, list):  # FastAPI validation errors: a list of {loc, msg, ...}
        parts: list[str] = []
        for item in detail:
            loc = item.get("loc") or ["request"]
            msg = str(item.get("msg", "")).removeprefix("Value error, ")
            parts.append(f"{loc[-1]}: {msg}")
        return "; ".join(parts)
    constraint = body.get("constraint")  # set by the backend's DB error handlers
    return f"{detail} ({constraint})" if constraint else str(detail)


class ApiClient:
    def __init__(self, base_url: str, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
        # Generous timeout: the first request after Neon autosuspends can be slow.
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(30.0, connect=10.0),
            transport=transport,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            resp = await self._http.request(method, path, params=clean, json=json)
        except httpx.TransportError as exc:
            raise ApiError(0, f"Cannot reach the API at {self._http.base_url}") from exc
        if resp.status_code == 204:
            return None
        if resp.is_success:
            return resp.json()
        raise ApiError(resp.status_code, _error_message(resp))

    async def aclose(self) -> None:
        await self._http.aclose()


# ---------------------------------------------------------------------------
# Modals
# ---------------------------------------------------------------------------


class ConfirmScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmScreen { align: center middle; }
    ConfirmScreen > Vertical {
        width: 60; height: auto; padding: 1 2;
        border: thick $error; background: $surface;
    }
    ConfirmScreen Horizontal { height: auto; margin-top: 1; align-horizontal: right; }
    """
    BINDINGS = [  # noqa: RUF012
        Binding("y", "answer(True)", "Yes"),
        Binding("n,escape", "answer(False)", "No"),
    ]

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(Text(self.question))
            with Horizontal():
                yield Button("No (n)", id="no")
                yield Button("Yes (y)", id="yes", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_answer(self, answer: bool) -> None:
        self.dismiss(answer)


class ApplicationForm(ModalScreen[bool]):
    """Add/edit form. Stays open if the API rejects the input, so nothing typed is lost."""

    DEFAULT_CSS = """
    ApplicationForm { align: center middle; }
    ApplicationForm > Vertical {
        width: 70; height: 90%; padding: 0 2;
        border: thick $primary; background: $surface;
    }
    ApplicationForm VerticalScroll { height: 1fr; }
    ApplicationForm #heading { margin-bottom: 1; }
    ApplicationForm #error { color: $error; height: auto; }
    ApplicationForm Horizontal { height: auto; align-horizontal: right; }
    """
    BINDINGS = [Binding("escape", "cancel", "Cancel")]  # noqa: RUF012
    AUTO_FOCUS = "#company_name"  # otherwise the scroll container grabs focus first

    TEXT_FIELDS = ["company_name", "role_title", "date_applied", "recruiter_email", "notes"]  # noqa: RUF012

    def __init__(
        self,
        heading: str,
        existing: Row | None,
        save_callback: Callable[[Row], Awaitable[None]],
    ) -> None:
        super().__init__()
        self.heading = heading
        self.existing = existing
        self.save_callback = save_callback
        self.is_saving = False

    def compose(self) -> ComposeResult:
        row = self.existing or {}
        # New applications default to "Applied today"; edits show what's stored.
        default_date = "" if self.existing else date.today().isoformat()
        with Vertical():
            yield Label(Text(self.heading, style="bold"), id="heading")
            # Fields scroll if the terminal is short; the buttons below stay pinned.
            with VerticalScroll():
                yield Label("Company *")
                yield Input(row.get("company_name") or "", id="company_name")
                yield Label("Role *")
                yield Input(row.get("role_title") or "", id="role_title")
                yield Label("Status")
                yield Select(
                    [(s, s) for s in STATUSES],
                    value=row.get("status", "Applied"),
                    allow_blank=False,
                    id="status",
                )
                yield Label("Date applied (YYYY-MM-DD, required unless 'Not Applied')")
                yield Input(row.get("date_applied") or default_date, id="date_applied")
                yield Label("Recruiter email")
                yield Input(row.get("recruiter_email") or "", id="recruiter_email")
                yield Label("Notes")
                yield Input(row.get("notes") or "", id="notes")
            yield Static("", id="error")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
        else:
            self.run_worker(self.save(), exclusive=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.run_worker(self.save(), exclusive=True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def show_error(self, message: str) -> None:
        self.query_one("#error", Static).update(Text(message))

    async def save(self) -> None:
        if self.is_saving:
            return

        # Empty text becomes None so optional fields are cleared rather than set to "".
        values: Row = {
            field: self.query_one(f"#{field}", Input).value.strip() or None
            for field in self.TEXT_FIELDS
        }
        values["status"] = str(self.query_one("#status", Select).value)

        # Same rules the backend enforces, checked here for a quicker, cleaner message.
        if not values["company_name"] or not values["role_title"]:
            self.show_error("Company and role are required.")
            return
        if values["date_applied"]:
            try:
                date.fromisoformat(values["date_applied"])
            except ValueError:
                self.show_error("Date applied must look like 2026-10-15.")
                return
        elif values["status"] != "Not Applied":
            self.show_error("Date applied is required unless the status is 'Not Applied'.")
            return

        self.is_saving = True
        self.query_one("#save", Button).disabled = True
        try:
            await self.save_callback(values)
        except ApiError as err:
            self.show_error(str(err))
            self.is_saving = False
            self.query_one("#save", Button).disabled = False
        else:
            self.dismiss(True)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


class JamApp(App[None]):
    TITLE = "JAM - Applications"
    CSS = """
    #search { margin: 1 1 0 1; }
    DataTable { height: 1fr; margin: 1; }
    """
    BINDINGS = [  # noqa: RUF012
        Binding("n", "new_application", "New"),
        Binding("e", "edit_application", "Edit"),
        Binding("d", "delete_application", "Delete"),
        Binding("r", "reload", "Refresh"),
        Binding("slash", "focus_search", "Search"),
    ]

    def __init__(self) -> None:
        super().__init__()
        load_dotenv()
        self.api = ApiClient(os.getenv("JAM_API_URL", "http://localhost:8000"))
        self.student_id = int(os.getenv("JAM_STUDENT_ID", "1"))
        self.search_text = ""
        self.applications: dict[int, Row] = {}

    # -- layout -------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search company or role, then press Enter", id="search")
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = f"student {self.student_id}"
        table = self.query_one(DataTable)
        table.add_columns("Company", "Role", "Status", "Applied")
        table.focus()
        self.load()

    async def on_unmount(self) -> None:
        await self.api.aclose()

    # -- reading ------------------------------------------------------------

    @work(exclusive=True)
    async def load(self) -> None:
        """Fetch this student's applications (filtered by the search box) into the table."""
        table = self.query_one(DataTable)
        table.loading = True
        try:
            rows: list[Row] = await self.api.request(
                "GET",
                "/applications",
                params={
                    "student_id": self.student_id,
                    "q": self.search_text or None,
                    "limit": PAGE_SIZE,
                },
            )
        except ApiError as err:
            self.notify(str(err), severity="error", timeout=8)
            return
        finally:
            table.loading = False

        selected = self.selected_id()
        self.applications = {row["application_id"]: row for row in rows}
        table.clear()
        for row in rows:
            # Text(...) so brackets in user data aren't parsed as Rich markup.
            table.add_row(
                Text(row["company_name"]),
                Text(row["role_title"]),
                Text(row["status"]),
                Text(row["date_applied"] or "-"),
                key=str(row["application_id"]),
            )
        if selected in self.applications:
            table.move_cursor(row=table.get_row_index(str(selected)))
        self.sub_title = f"student {self.student_id} · {len(rows)} application(s)"

    def selected_id(self) -> int | None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return None
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        return int(row_key.value) if row_key.value is not None else None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.search_text = event.value.strip()
            self.query_one(DataTable).focus()
            self.load()

    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_reload(self) -> None:
        self.load()

    # -- creating -----------------------------------------------------------

    def action_new_application(self) -> None:
        async def create(values: Row) -> None:
            await self.api.request(
                "POST", "/applications", json={"student_id": self.student_id, **values}
            )
            self.notify("Application added")

        self.push_screen(ApplicationForm("New application", None, create), self.after_save)

    # -- updating -----------------------------------------------------------

    def action_edit_application(self) -> None:
        app_id = self.selected_id()
        if app_id is None:
            self.notify("No application selected", severity="warning")
            return
        original = self.applications[app_id]

        async def update(values: Row) -> None:
            # Send only what changed. The backend rejects an empty PATCH with a 400.
            changes = {k: v for k, v in values.items() if v != original.get(k)}
            if changes:
                await self.api.request("PATCH", f"/applications/{app_id}", json=changes)
                self.notify("Application updated")

        self.push_screen(ApplicationForm("Edit application", original, update), self.after_save)

    def after_save(self, saved: bool | None) -> None:
        if saved:
            self.load()
        self.query_one(DataTable).focus()

    # -- deleting -----------------------------------------------------------

    def action_delete_application(self) -> None:
        app_id = self.selected_id()
        if app_id is None:
            self.notify("No application selected", severity="warning")
            return
        row = self.applications[app_id]

        def after_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self.delete_application(app_id)
            self.query_one(DataTable).focus()

        question = f"Delete {row['company_name']} - {row['role_title']}?"
        self.push_screen(ConfirmScreen(question), after_confirm)

    @work
    async def delete_application(self, app_id: int) -> None:
        try:
            await self.api.request("DELETE", f"/applications/{app_id}")
        except ApiError as err:
            if err.status_code == 409:
                self.notify(
                    "Can't delete: interviews or reminders still reference this application.",
                    severity="error",
                    timeout=8,
                )
            else:
                self.notify(str(err), severity="error", timeout=8)
            return
        self.notify("Application deleted")
        self.load()