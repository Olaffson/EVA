import sqlite3
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    eva_id INTEGER PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    full_name TEXT,
    is_public INTEGER,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stats_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eva_id INTEGER NOT NULL,
    captured_at TEXT DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT NOT NULL,
    FOREIGN KEY (eva_id) REFERENCES players (eva_id)
);
"""


def get_connection(path: Path = config.DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def upsert_player(conn, *, eva_id, username, display_name, full_name, is_public):
    conn.execute(
        """
        INSERT INTO players (eva_id, username, display_name, full_name, is_public)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(eva_id) DO UPDATE SET
            username=excluded.username,
            display_name=excluded.display_name,
            full_name=excluded.full_name,
            is_public=excluded.is_public,
            scraped_at=CURRENT_TIMESTAMP
        """,
        (eva_id, username, display_name, full_name, is_public),
    )
    conn.commit()


def insert_stats_snapshot(conn, *, eva_id, raw_json):
    conn.execute(
        "INSERT INTO stats_snapshots (eva_id, raw_json) VALUES (?, ?)",
        (eva_id, raw_json),
    )
    conn.commit()
