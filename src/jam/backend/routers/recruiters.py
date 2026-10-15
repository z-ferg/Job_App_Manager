"""Recruiters: list, get, create, update, delete."""

from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection
from pydantic import BaseModel

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

router = APIRouter(prefix="/recruiters", tags=["recruiters"])


class RecruiterCreate(BaseModel):
    company_id: int
    name: str
    email: str | None = None


class RecruiterUpdate(BaseModel):
    company_id: int | None = None
    name: str | None = None
    email: str | None = None


class RecruiterRead(RecruiterCreate):
    recruiter_id: int


@router.get("", response_model=list[RecruiterRead])
async def list_recruiters(
    company_id: int | None = None,
    q: str | None = Query(None, description="Search recruiter name"),
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("company_id = %s", company_id),
            ("name ILIKE %s", f"%{q}%" if q else None),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM recruiter {where} ORDER BY name LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{recruiter_id}", response_model=RecruiterRead)
async def get_recruiter(recruiter_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "recruiter", "recruiter_id", recruiter_id)


@router.post("", response_model=RecruiterRead, status_code=201)
async def create_recruiter(
    body: RecruiterCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "recruiter", body.model_dump())


@router.patch("/{recruiter_id}", response_model=RecruiterRead)
async def update_recruiter(
    recruiter_id: int, body: RecruiterUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn,
        "recruiter",
        "recruiter_id",
        recruiter_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{recruiter_id}", status_code=204)
async def delete_recruiter(
    recruiter_id: int, conn: AsyncConnection = Depends(get_conn)
):
    # job_listing.recruiter_id / interview.recruiter_id -> SET NULL;
    # event_recruiters rows -> CASCADE.
    await delete_row(conn, "recruiter", "recruiter_id", recruiter_id)
