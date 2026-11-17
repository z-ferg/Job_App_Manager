"""Database helpers: the pooled connection dependency; also small query utilities."""

from enum import Enum
from typing import Any

from fastapi import HTTPException, Query, Request
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


def make_pool(url: str) -> AsyncConnectionPool:
    """Build (but don't open) the connection pool."""
    return AsyncConnectionPool(
        url,
        min_size=1,
        max_size=5,
        open=False,  # opened explicitly in lifespan
        check=AsyncConnectionPool.check_connection,  # discards dead conns after Neon autosuspend
    )

async def get_conn(request: Request):
    """Yield one pooled connection per request"""
    async with request.app.state.pool.connection() as conn:
        yield conn


def pagination(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> tuple[int, int]:
    """Dependency returning (limit, offset)."""
    return limit, offset


def _adapt(value: Any) -> Any:
    """Convert Python enums to their raw value so Postgres can cast to its enum type."""
    return value.value if isinstance(value, Enum) else value


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

async def fetch_all(conn: AsyncConnection, query, params=()) -> list[dict]:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, [_adapt(p) for p in params])
        return await cur.fetchall()


async def fetch_one(conn: AsyncConnection, query, params=()) -> dict | None:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, [_adapt(p) for p in params])
        return await cur.fetchone()


async def get_row(conn: AsyncConnection, table: str, pk_col: str, pk: Any) -> dict:
    """SELECT * by primary key, or raise 404."""
    row = await fetch_one(
        conn,
        sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
            sql.Identifier(table), sql.Identifier(pk_col)
        ),
        (pk,),
    )
    if row is None:
        raise HTTPException(404, f"{table} {pk} not found")
    return row


def build_where(conds: list[tuple[str, Any]]) -> tuple[str, list]:
    """Build a WHERE clause from (sql_fragment_with_one_%s, value) pairs."""
    used = [(frag, val) for frag, val in conds if val is not None]
    if not used:
        return "", []
    return "WHERE " + " AND ".join(frag for frag, _ in used), [val for _, val in used]


# ---------------------------------------------------------------------------
# Writes (with commits)
# ---------------------------------------------------------------------------

async def insert_row(conn: AsyncConnection, table: str, data: dict) -> dict:
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, data)),
        sql.SQL(", ").join(sql.Placeholder() for _ in data),
    )
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, [_adapt(v) for v in data.values()])
        row = await cur.fetchone()
    await conn.commit()
    return row


async def update_row(
    conn: AsyncConnection, table: str, pk_col: str, pk: Any, data: dict
) -> dict:
    """Partial update from given fields. 400 if empty or 404 if its missing."""
    if not data:
        raise HTTPException(400, "No fields to update")
    query = sql.SQL("UPDATE {} SET {} WHERE {} = %s RETURNING *").format(
        sql.Identifier(table),
        sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col)) for col in data
        ),
        sql.Identifier(pk_col),
    )
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, [*(_adapt(v) for v in data.values()), pk])
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(404, f"{table} {pk} not found")
    await conn.commit()
    return row


async def delete_row(conn: AsyncConnection, table: str, pk_col: str, pk: Any) -> None:
    query = sql.SQL("DELETE FROM {} WHERE {} = %s RETURNING 1").format(
        sql.Identifier(table), sql.Identifier(pk_col)
    )
    async with conn.cursor() as cur:
        await cur.execute(query, (pk,))
        deleted = await cur.fetchone()
    if deleted is None:
        raise HTTPException(404, f"{table} {pk} not found")
    await conn.commit()


async def execute_write(conn: AsyncConnection, query, params=()) -> int:
    """Run a write statement, commit, and return the affected row count."""
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        count = cur.rowcount
    await conn.commit()
    return count
