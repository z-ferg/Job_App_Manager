"""Event registrations: students registering for career fair events."""

from datetime import date

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

from jam.backend.db import (
    build_where,
    delete_row,
    fetch_all,
    get_conn,
    get_row,
    insert_row,
    pagination,
    update_row,
)

router = APIRouter(prefix="/event-registrations", tags=["event registrations"])


class RegistrationCreate(BaseModel):
    student_id: int
    event_id: int
    registration_date: date = Field(default_factory=date.today)
    match_score: float | None = None


class RegistrationUpdate(BaseModel):
    # student_id / event_id are the identity of a registration, so they aren't editable.
    registration_date: date | None = None
    match_score: float | None = None


class RegistrationRead(RegistrationCreate):
    registration_id: int


@router.get("", response_model=list[RegistrationRead])
async def list_registrations(
    student_id: int | None = None,
    event_id: int | None = None,
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [("student_id = %s", student_id), ("event_id = %s", event_id)]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM event_registration {where} "
        "ORDER BY registration_date DESC, registration_id DESC LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{registration_id}", response_model=RegistrationRead)
async def get_registration(
    registration_id: int, conn: AsyncConnection = Depends(get_conn)
):
    return await get_row(conn, "event_registration", "registration_id", registration_id)


@router.post("", response_model=RegistrationRead, status_code=201)
async def create_registration(
    body: RegistrationCreate, conn: AsyncConnection = Depends(get_conn)
):
    # 409 if the student is already registered for this event (uq_registration_student_event).
    return await insert_row(conn, "event_registration", body.model_dump())


@router.patch("/{registration_id}", response_model=RegistrationRead)
async def update_registration(
    registration_id: int,
    body: RegistrationUpdate,
    conn: AsyncConnection = Depends(get_conn),
):
    return await update_row(
        conn,
        "event_registration",
        "registration_id",
        registration_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{registration_id}", status_code=204)
async def delete_registration(
    registration_id: int, conn: AsyncConnection = Depends(get_conn)
):
    # 409 if reminders still point at this registration.
    await delete_row(conn, "event_registration", "registration_id", registration_id)
