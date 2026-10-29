"""Database interface for the Job Application Manager (JAM).

Exposes a FastAPI application with endpoints for interacting with the
PostgreSQL database hosted on Neon.

All of the database interaction code lives in this module.
"""

import os
from contextlib import asynccontextmanager

from backend.routers import applications, companies, events, interviews, job_listings, recruiters, registrations, reminders
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import make_pool

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATABASE_URL: str = ""  # loaded from .env


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Open a single async psycopg connection on startup, close it on shutdown."""
    global DATABASE_URL
    from dotenv import load_dotenv

    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set — create a .env file")

    application.state.pool = make_pool(DATABASE_URL)

    await application.state.pool.open()
    yield
    await application.state.pool.close()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="JAM API",
        description="Job Application Manager — RESTful API for the Neon-hosted PostgreSQL schema.",
        version="0.0.1",
        lifespan=lifespan,
    )

    # CORS: allow the localhost dev servers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://localhost:3000", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    from backend.errors import register_error_handlers
    from backend.routers import (
        auth,
        students,
    )

    register_error_handlers(app)
    for module in (
        applications, auth, companies, events, interviews, job_listings,
        recruiters, registrations, reminders, students
    ):
        app.include_router(module.router)

    return app


app = create_app()
