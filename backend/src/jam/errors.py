"""Translate Postgres constraint violations into clean HTTP errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg import errors as pgerr


def _make_handler(status_code: int, message: str):
    async def handler(request: Request, exc: pgerr.Error) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": message,
                # e.g. "uq_application_student_listing" or "chk_application_date_applied"
                "constraint": exc.diag.constraint_name or exc.diag.column_name,
            },
        )

    return handler


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        pgerr.UniqueViolation, _make_handler(409, "Already exists")
    )
    app.add_exception_handler(
        pgerr.ForeignKeyViolation,
        _make_handler(409, "Referenced row does not exist, or row is still referenced"),
    )
    app.add_exception_handler(
        pgerr.CheckViolation, _make_handler(422, "Check constraint failed")
    )
    app.add_exception_handler(
        pgerr.NotNullViolation, _make_handler(422, "A required field was null")
    )
