import os
from pathlib import Path

DATABASE_URL: str | None = os.environ.get("DATABASE_URL")
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DATA_DIR / "bugs.db"

# Populated at startup by connect_db()
_pool = None  # asyncpg pool (Postgres)
_conn = None  # aiosqlite connection (SQLite)

CREATE_BUGS_TABLE_SQLITE = """
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    email TEXT,
    category TEXT NOT NULL DEFAULT 'Other',
    created_at TEXT NOT NULL
);
"""

CREATE_BUGS_TABLE_PG = """
CREATE TABLE IF NOT EXISTS bugs (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    email TEXT,
    category TEXT NOT NULL DEFAULT 'Other',
    created_at TEXT NOT NULL
);
"""


async def connect_db():
    global _pool, _conn

    if DATABASE_URL:
        import asyncpg

        print(f"[DB] Connecting to PostgreSQL (URL length: {len(DATABASE_URL)})")
        _pool = await asyncpg.create_pool(DATABASE_URL, statement_cache_size=0)
        async with _pool.acquire() as conn:
            await conn.execute(CREATE_BUGS_TABLE_PG)
        print("[DB] PostgreSQL connected and bugs table ready")
    else:
        import aiosqlite

        print("[DB] DATABASE_URL not set, falling back to SQLite")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _conn = await aiosqlite.connect(DB_PATH)
        _conn.row_factory = aiosqlite.Row
        await _conn.execute(CREATE_BUGS_TABLE_SQLITE)
        await _conn.commit()
        print(f"[DB] SQLite connected at {DB_PATH}")


async def close_db():
    global _pool, _conn

    if _pool is not None:
        await _pool.close()
        _pool = None
    if _conn is not None:
        await _conn.close()
        _conn = None


async def insert_bug(description: str, email: str | None, category: str, created_at: str) -> int:
    if _pool is not None:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO bugs (description, email, category, created_at) "
                "VALUES ($1, $2, $3, $4) RETURNING id",
                description, email, category, created_at,
            )
            return row["id"]
    else:
        cursor = await _conn.execute(
            "INSERT INTO bugs (description, email, category, created_at) VALUES (?, ?, ?, ?)",
            (description, email, category, created_at),
        )
        await _conn.commit()
        return cursor.lastrowid


async def fetch_bugs() -> list[dict]:
    if _pool is not None:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM bugs ORDER BY id DESC")
            return [dict(row) for row in rows]
    else:
        cursor = await _conn.execute("SELECT * FROM bugs ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "description": row["description"],
                "email": row["email"],
                "category": row["category"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
