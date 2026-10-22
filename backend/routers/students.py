"""Student data: list, get, create, update, delete."""

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

router = APIRouter(prefix="/students", tags=["students"])


class StudentCreate(BaseModel):
    name: str
    email: str
    university: str
    major: str
    grad_year: int = Field(ge=2000, le=2100)  # mirrors chk_student_grad_year


class StudentUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    university: str | None = None
    major: str | None = None
    grad_year: int | None = Field(None, ge=2000, le=2100)


class StudentRead(StudentCreate):
    student_id: int


@router.get("", response_model=list[StudentRead])
async def list_students(
    q: str | None = Query(None, description="Search name or email"),
    university: str | None = None,
    major: str | None = None,
    grad_year: int | None = None,
    page: tuple[int, int] = Depends(pagination),
    conn: AsyncConnection = Depends(get_conn),
):
    where, params = build_where(
        [
            ("(name || ' ' || email) ILIKE %s", f"%{q}%" if q else None),
            ("university = %s", university),
            ("major = %s", major),
            ("grad_year = %s", grad_year),
        ]
    )
    return await fetch_all(
        conn,
        f"SELECT * FROM student {where} ORDER BY name LIMIT %s OFFSET %s",
        [*params, *page],
    )


@router.get("/{student_id}", response_model=StudentRead)
async def get_student(student_id: int, conn: AsyncConnection = Depends(get_conn)):
    return await get_row(conn, "student", "student_id", student_id)


@router.post("", response_model=StudentRead, status_code=201)
async def create_student(
    body: StudentCreate, conn: AsyncConnection = Depends(get_conn)
):
    return await insert_row(conn, "student", body.model_dump())


@router.patch("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: int, body: StudentUpdate, conn: AsyncConnection = Depends(get_conn)
):
    return await update_row(
        conn, "student", "student_id", student_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: int, conn: AsyncConnection = Depends(get_conn)):
    await delete_row(conn, "student", "student_id", student_id)
