"""Подключение к SQLite (aiosqlite)."""

from __future__ import annotations

from pathlib import Path

import aiosqlite


async def open_connection(db_path: Path) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    return conn
