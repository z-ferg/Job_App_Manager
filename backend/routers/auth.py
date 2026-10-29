"""Authentication: verify a student's email and password."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from pydantic import BaseModel

from backend.db import fetch_one, get_conn
from backend.routers.students import StudentRead

router = APIRouter(prefix="/auth", tags=["auth"])

_hasher = PasswordHasher()


class LoginRequest(BaseModel):
    email: str
    password: str


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
