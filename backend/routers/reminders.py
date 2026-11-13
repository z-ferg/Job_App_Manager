"""Reminders: CRUD with filters. Each reminder targets exactly one of
an application, an interview, or an event registration."""

from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from pydantic import BaseModel, model_validator

from backend.db import (
    build_where,
    delete_row,
    fetch_all,
    get_conn,
    get_row,
    insert_row,
    pagination,
    update_row,
)

router = APIRouter(prefix="/reminders", tags=["reminders"])


class ReminderType(str, Enum):
    FOLLOW_UP = "Follow-up"
    INTERVIEW_PREP = "Interview Prep"
    DEADLINE = "Deadline"
    EVENT_APPLICATION = "Event Application"


class ReminderCreate(BaseModel):
    application_id: int | None = None
    interview_id: int | None = None
    registration_id: int | None = None
    reminder_date: datetime
    reminder_type: ReminderType
    completed: bool = False

    @model_validator(mode="after")
    def exactly_one_target(self):
        # Mirrors chk_reminder_exactly_one_target.
        targets = [self.application_id, self.interview_id, self.registration_id]
        if sum(t is not None for t in targets) != 1:
            raise ValueError(
                "Provide exactly one of application_id, interview_id, registration_id"
            )
        return self


class ReminderUpdate(BaseModel):
    # The target is fixed at creation; delete and recreate to retarget.
    reminder_date: datetime | None = None
    reminder_type: ReminderType | None = None
    completed: bool | None = None


class ReminderRead(BaseModel):
    reminder_id: int
    application_id: int | None = None
    interview_id: int | None = None
    registration_id: int | None = None
    reminder_date: datetime
    reminder_type: ReminderType
    completed: bool
    # Only filled by the list endpoint: "Company · Role" or the event name.
    target_label: str | None = None


@router.get("", response_model=list[ReminderRead])
async def list_reminders(
    student_id: int | None = None,
    application_id: int | None = None,
    interview_id: int | None = None,
    registration_id: int | None = None,
    completed: bool | None = None,
    due_before: datetime | None = None,
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    """e.g. overdue: `?completed=false&due_before=<now>`."""
    # reminder has no student_id; ownership comes from whichever target it points at.
    where, params = build_where(
        [
            ("COALESCE(a.student_id, ia.student_id, er.student_id) = %s", student_id),
            ("r.application_id = %s", application_id),
            ("r.interview_id = %s", interview_id),
            ("r.registration_id = %s", registration_id),
            ("r.completed = %s", completed),
            ("r.reminder_date <= %s", due_before),
        ]
    )
    return await fetch_all(
        conn,
        f"""
        SELECT r.*,
               COALESCE(a.company_name || ' · ' || a.role_title,
                        ia.company_name || ' · ' || ia.role_title,
                        e.event_name) AS target_label
        FROM reminder r
        LEFT JOIN application a ON a.application_id = r.application_id
        LEFT JOIN interview i ON i.interview_id = r.interview_id
        LEFT JOIN application ia ON ia.application_id = i.application_id
        LEFT JOIN event_registration er ON er.registration_id = r.registration_id
        LEFT JOIN career_fair_event e ON e.event_id = er.event_id
        {where}
        ORDER BY r.reminder_date, r.reminder_id LIMIT %s OFFSET %s
        """,
        [*params, *page],
    )


@router.get("/{reminder_id}", response_model=ReminderRead)
async def get_reminder(reminder_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "reminder", "reminder_id", reminder_id)


@router.post("", response_model=ReminderRead, status_code=201)
async def create_reminder(
    body: ReminderCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "reminder", body.model_dump(exclude_none=True))


@router.patch("/{reminder_id}", response_model=ReminderRead)
async def update_reminder(
    reminder_id: int, body: ReminderUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn,
        "reminder",
        "reminder_id",
        reminder_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(reminder_id: int, conn: AsyncConnection = Depends(get_conn)):
    await delete_row(conn, "reminder", "reminder_id", reminder_id)
