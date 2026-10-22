"""Job listings: list (with filters), get, create, update, delete."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection
from pydantic import BaseModel, Field, model_validator

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

router = APIRouter(prefix="/job-listings", tags=["job listings"])


class ListingBase(BaseModel):
    recruiter_id: int | None = None
    company_id: int
    title: str
    description: str
    requirements: str
    posted_date: date = Field(default_factory=date.today)
    deadline: date | None = None


class ListingCreate(ListingBase):
    @model_validator(mode="after")
    def deadline_not_before_posted(self):
        if self.deadline is not None and self.deadline < self.posted_date:
            raise ValueError("deadline cannot be before posted_date")
        return self


class ListingUpdate(BaseModel):
    recruiter_id: int | None = None
    company_id: int | None = None
    title: str | None = None
    description: str | None = None
    requirements: str | None = None
    posted_date: date | None = None
    deadline: date | None = None


class ListingRead(ListingBase):
    listing_id: int


@router.get("", response_model=list[ListingRead])
async def list_listings(
    company_id: int | None = None,
    recruiter_id: int | None = None,
    open_only: bool = Query(False, description="Only listings with no deadline or a future deadline"),
    q: str | None = Query(None, description="Search title"),
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("company_id = %s", company_id),
            ("recruiter_id = %s", recruiter_id),
            (
                "(deadline IS NULL OR deadline >= %s)",
                date.today() if open_only else None,
            ),
            ("title ILIKE %s", f"%{q}%" if q else None),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM job_listing {where} "
        "ORDER BY posted_date DESC, listing_id DESC LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{listing_id}", response_model=ListingRead)
async def get_listing(listing_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "job_listing", "listing_id", listing_id)


@router.post("", response_model=ListingRead, status_code=201)
async def create_listing(
    body: ListingCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "job_listing", body.model_dump())


@router.patch("/{listing_id}", response_model=ListingRead)
async def update_listing(
    listing_id: int, body: ListingUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn,
        "job_listing",
        "listing_id",
        listing_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{listing_id}", status_code=204)
async def delete_listing(listing_id: int, conn: AsyncConnection = Depends(get_conn)):
    # 409 if any application still references this listing.
    await delete_row(conn, "job_listing", "listing_id", listing_id)
