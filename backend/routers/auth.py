"""Authentication: verify a student's email and password."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

from backend.db import fetch_one, get_conn, insert_row
from backend.routers.students import StudentCreate, StudentRead

router = APIRouter(prefix="/auth", tags=["auth"])

_hasher = PasswordHasher()


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(StudentCreate):
    password: str = Field(min_length=8)


@router.post("/signup", response_model=StudentRead, status_code=201)
async def signup(body: SignupRequest, conn: AsyncConnection = Depends(get_conn)):
    # The unique constraint on email is case-sensitive, but login matches case-insensitively.
    existing = await fetch_one(
        conn, "SELECT 1 FROM student WHERE lower(email) = lower(%s)", [body.email]
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with that email already exists")

    data = body.model_dump(exclude={"password"})
    data["password_hash"] = _hasher.hash(body.password)
    return await insert_row(conn, "student", data)


@router.post("/login", response_model=StudentRead)
async def login(body: LoginRequest, conn: AsyncConnection = Depends(get_conn)):
    student = await fetch_one(
        conn, "SELECT * FROM student WHERE lower(email) = lower(%s)", [body.email]
    )

    # Same error for unknown email and wrong password, so callers can't probe for accounts.
    try:
        if student is None:
            raise VerifyMismatchError
        _hasher.verify(student["password_hash"], body.password)
    except (VerifyMismatchError, InvalidHashError):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # StudentRead has no password_hash field, so the hash is never sent back.
    return student
