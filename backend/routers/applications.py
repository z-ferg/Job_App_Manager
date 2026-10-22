"""Applications: the core resource. CRUD, filters, listing autofill, status summary."""

from datetime import date
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import AsyncConnection
from pydantic import BaseModel, model_validator

from backend.db import (
    build_where,
    delete_row,
    fetch_all,
    fetch_one,
    get_conn,
    get_row,
    insert_row,
    pagination,
    update_row,
)

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationStatus(str, Enum):
    """Values must match the Postgres application_status enum labels exactly."""

    NOT_APPLIED = "Not Applied"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class ApplicationCreate(BaseModel):
    student_id: int
    # Either pick a listing (company/role are filled from it) ...
    listing_id: int | None = None
    # ... or enter one manually with a role_title and company_name or company_id.
    company_id: int | None = None
    company_name: str | None = None
    role_title: str | None = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    date_applied: date | None = None
    recruiter_email: str | None = None
    notes: str | None = None
    last_followup_date: date | None = None

    @model_validator(mode="after")
    def check_rules(self):
        # Mirrors chk_application_date_applied so the client gets a clean 422.
        if self.status != ApplicationStatus.NOT_APPLIED and self.date_applied is None:
            raise ValueError("date_applied is required unless status is 'Not Applied'")
        if self.listing_id is None:
            if not self.role_title:
                raise ValueError("role_title is required when listing_id is not given")
            if not self.company_name and self.company_id is None:
                raise ValueError(
                    "company_name or company_id is required when listing_id is not given"
                )
        return self


class ApplicationUpdate(BaseModel):
    # student_id / listing_id are the identity of an application, so they aren't editable.
    company_name: str | None = None
    role_title: str | None = None
    status: ApplicationStatus | None = None
    date_applied: date | None = None
    recruiter_email: str | None = None
    notes: str | None = None
    last_followup_date: date | None = None


class ApplicationRead(BaseModel):
    application_id: int
    student_id: int
    listing_id: int | None = None
    company_id: int | None = None
    company_name: str
    role_title: str
    status: ApplicationStatus
    date_applied: date | None = None
    recruiter_email: str | None = None
    notes: str | None = None
    last_followup_date: date | None = None


class StatusCount(BaseModel):
    status: ApplicationStatus
    count: int


@router.get("", response_model=list[ApplicationRead])
async def list_applications(
    student_id: int | None = None,
    status: ApplicationStatus | None = None,
    company_id: int | None = None,
    q: str | None = Query(None, description="Search company name or role title"),
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("student_id = %s", student_id),
            ("status = %s", status.value if status else None),
            ("company_id = %s", company_id),
            ("(company_name || ' ' || role_title) ILIKE %s", f"%{q}%" if q else None),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM application {where} "
        "ORDER BY date_applied DESC NULLS LAST, application_id DESC LIMIT %s OFFSET %s",
        [*params, *page],
    )


# NOTE: declared before "/{application_id}" so "summary" isn't parsed as an id.
@router.get("/summary", response_model=list[StatusCount])
async def status_summary(
    student_id: int | None = None, conn: AsyncConnection = Depends(get_conn)
):
    """Application counts grouped by status (handy for a dashboard)."""
    where, params = build_where([("student_id = %s", student_id)])
    return await fetch_all(
        conn,
        f"""
        SELECT status::text AS status, COUNT(*)::int AS count
        FROM application {where}
        GROUP BY application.status
        ORDER BY application.status
        """,
        params,
    )


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int, conn: AsyncConnection = Depends(get_conn)
):
    return await get_row(conn, "application", "application_id", application_id)


@router.post("", response_model=ApplicationRead, status_code=201)
async def create_application(
    body: ApplicationCreate, conn: AsyncConnection = Depends(get_conn)
):
    data = body.model_dump(exclude_none=True)

    if body.listing_id is not None:
        listing = await fetch_one(
            conn,
            """
            SELECT l.company_id, l.title, c.company_name
            FROM job_listing l
            JOIN company c ON c.company_id = l.company_id
            WHERE l.listing_id = %s
            """,
            (body.listing_id,),
        )
        if listing is None:
            raise HTTPException(404, f"job_listing {body.listing_id} not found")
        # Anything the client sent explicitly wins; the listing fills the gaps.
        data.setdefault("company_id", listing["company_id"])
        data.setdefault("company_name", listing["company_name"])
        data.setdefault("role_title", listing["title"])
    elif "company_name" not in data:
        company = await get_row(conn, "company", "company_id", body.company_id)
        data["company_name"] = company["company_name"]

    # 409 if this student already applied to this listing (uq_application_student_listing).
    return await insert_row(conn, "application", data)


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: int,
    body: ApplicationUpdate,
    conn: AsyncConnection = Depends(get_conn),
):
    # Moving an application out of 'Not Applied' without a date_applied on the row
    # trips chk_application_date_applied (returned as a 422 by the error handler).
    return await update_row(
        conn,
        "application",
        "application_id",
        application_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{application_id}", status_code=204)
async def delete_application(
    application_id: int, conn: AsyncConnection = Depends(get_conn)
):
    # 409 if interviews or reminders still reference this application.
    await delete_row(conn, "application", "application_id", application_id)
