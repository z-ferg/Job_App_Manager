"""Companies: list, get, create, update, delete."""

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

router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyCreate(BaseModel):
    company_name: str
    industry: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    website: str | None = None


class CompanyRead(CompanyCreate):
    company_id: int


@router.get("", response_model=list[CompanyRead])
async def list_companies(
    q: str | None = Query(None, description="Search company name"),
    industry: str | None = None,
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("company_name ILIKE %s", f"%{q}%" if q else None),
            ("industry = %s", industry),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM company {where} ORDER BY company_name LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "company", "company_id", company_id)


@router.post("", response_model=CompanyRead, status_code=201)
async def create_company(
    body: CompanyCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "company", body.model_dump())


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int, body: CompanyUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn, "company", "company_id", company_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: int, conn: AsyncConnection = Depends(get_conn)):
    await delete_row(conn, "company", "company_id", company_id)
