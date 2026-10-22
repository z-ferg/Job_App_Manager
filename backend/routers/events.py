"""Career fair events: CRUD, plus attaching recruiters (event_recruiters junction)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import AsyncConnection
from pydantic import BaseModel

from backend.db import (
    build_where,
    delete_row,
    execute_write,
    fetch_all,
    get_conn,
    get_row,
    insert_row,
    pagination,
    update_row,
)

router = APIRouter(prefix="/events", tags=["events"])


class EventCreate(BaseModel):
    event_name: str
    event_date: datetime | None = None
    location: str | None = None
    description: str | None = None


class EventUpdate(BaseModel):
    event_name: str | None = None
    event_date: datetime | None = None
    location: str | None = None
    description: str | None = None


class EventRead(EventCreate):
    event_id: int


class EventRecruiter(BaseModel):
    recruiter_id: int
    company_id: int
    company_name: str
    name: str
    email: str | None = None


@router.get("", response_model=list[EventRead])
async def list_events(
    upcoming_only: bool = Query(False, description="Only events from now onward"),
    q: str | None = Query(None, description="Search event name"),
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("event_date >= %s", datetime.now() if upcoming_only else None),
            ("event_name ILIKE %s", f"%{q}%" if q else None),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM career_fair_event {where} "
        "ORDER BY event_date NULLS LAST, event_id LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "career_fair_event", "event_id", event_id)


@router.post("", response_model=EventRead, status_code=201)
async def create_event(body: EventCreate, conn: AsyncConnection = Depends(get_conn)):
    return await insert_row(conn, "career_fair_event", body.model_dump())


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int, body: EventUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn,
        "career_fair_event",
        "event_id",
        event_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: int, conn: AsyncConnection = Depends(get_conn)):
    # event_recruiters rows cascade; 409 if students are still registered.
    await delete_row(conn, "career_fair_event", "event_id", event_id)


# ---------------------------------------------------------------------------
# Recruiters attending an event
# ---------------------------------------------------------------------------

@router.get("/{event_id}/recruiters", response_model=list[EventRecruiter])
async def list_event_recruiters(
    event_id: int, conn: AsyncConnection = Depends(get_conn)
):
    await get_row(conn, "career_fair_event", "event_id", event_id)  # 404 if missing
    return await fetch_all(
        conn,
        """
        SELECT r.recruiter_id, r.company_id, c.company_name, r.name, r.email
        FROM event_recruiters er
        JOIN recruiter r ON r.recruiter_id = er.recruiter_id
        JOIN company c ON c.company_id = r.company_id
        WHERE er.event_id = %s
        ORDER BY c.company_name, r.name
        """,
        (event_id,),
    )


@router.put("/{event_id}/recruiters/{recruiter_id}", status_code=204)
async def add_event_recruiter(
    event_id: int, recruiter_id: int, conn: AsyncConnection = Depends(get_conn)
):
    """Attach a recruiter to an event. Idempotent."""
    await get_row(conn, "career_fair_event", "event_id", event_id)
    await get_row(conn, "recruiter", "recruiter_id", recruiter_id)
    await execute_write(
        conn,
        "INSERT INTO event_recruiters (recruiter_id, event_id) VALUES (%s, %s) "
        "ON CONFLICT DO NOTHING",
        (recruiter_id, event_id),
    )


@router.delete("/{event_id}/recruiters/{recruiter_id}", status_code=204)
async def remove_event_recruiter(
    event_id: int, recruiter_id: int, conn: AsyncConnection = Depends(get_conn)
):
    removed = await execute_write(
        conn,
        "DELETE FROM event_recruiters WHERE event_id = %s AND recruiter_id = %s",
        (event_id, recruiter_id),
    )
    if removed == 0:
        raise HTTPException(404, "Recruiter is not attached to this event")
