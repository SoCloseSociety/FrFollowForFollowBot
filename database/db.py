from __future__ import annotations
import aiosqlite
from pathlib import Path
from config import settings
from database.models import TABLES_SQL

_db: aiosqlite.Connection | None = None

async def init_db() -> None:
    global _db
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _db = await aiosqlite.connect(str(db_path))
    _db.row_factory = aiosqlite.Row

    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")
    await _db.execute("PRAGMA busy_timeout=5000")

    for sql in TABLES_SQL:
        await _db.execute(sql)
    await _db.commit()

async def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db

async def close_db() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None