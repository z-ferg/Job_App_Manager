"""Interviews: CRUD with filters by application, student, and upcoming."""

from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

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

router = APIRouter(prefix="/interviews", tags=["interviews"])


class InterviewModality(str, Enum):
    PHONE = "Phone"
    VIDEO = "Video"
    IN_PERSON = "In Person"


class InterviewType(str, Enum):
    BEHAVIORAL = "Behavioral"
    TECHNICAL = "Technical"
    SCREENING = "Screening"


class InterviewCreate(BaseModel):
    application_id: int
    recruiter_id: int | None = None
    round_num: int = Field(1, ge=1)  # mirrors chk_interview_round
    interview_modality: InterviewModality
    interview_type: InterviewType
    interview_date: datetime | None = None
    notes: str | None = None


class InterviewUpdate(BaseModel):
    # application_id is the identity of an interview, so it isn't editable.
    recruiter_id: int | None = None
    round_num: int | None = Field(None, ge=1)
    interview_modality: InterviewModality | None = None
    interview_type: InterviewType | None = None
    interview_date: datetime | None = None
    notes: str | None = None


class InterviewRead(InterviewCreate):
    interview_id: int


@router.get("", response_model=list[InterviewRead])
async def list_interviews(
    application_id: int | None = None,
    student_id: int | None = Query(None, description="Interviews for this student's applications"),
    upcoming_only: bool = Query(False, description="Only interviews from now onward"),
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("i.application_id = %s", application_id),
            ("a.student_id = %s", student_id),
            ("i.interview_date >= %s", datetime.now() if upcoming_only else None),
        ]
    )
    return await fetch_all(
        conn,
        f"""
        SELECT i.*
        FROM interview i
        JOIN application a ON a.application_id = i.application_id
        {where}
        ORDER BY i.interview_date NULLS LAST, i.interview_id
        LIMIT %s OFFSET %s
        """,
        [*params, *page],
    )


@router.get("/{interview_id}", response_model=InterviewRead)
async def get_interview(interview_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "interview", "interview_id", interview_id)


@router.post("", response_model=InterviewRead, status_code=201)
async def create_interview(
    body: InterviewCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "interview", body.model_dump())


@router.patch("/{interview_id}", response_model=InterviewRead)
async def update_interview(
    interview_id: int, body: InterviewUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn,
        "interview",
        "interview_id",
        interview_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{interview_id}", status_code=204)
async def delete_interview(
    interview_id: int, conn: AsyncConnection = Depends(get_conn)
):
    # 409 if reminders still reference this interview.
    await delete_row(conn, "interview", "interview_id", interview_id)
