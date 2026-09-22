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

CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY,
    season_id INTEGER NOT NULL,
    game_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    mode_id INTEGER,
    mode_identifier TEXT,
    map_id INTEGER,
    map_name TEXT
);

CREATE TABLE IF NOT EXISTS game_players (
    game_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    is_mvp INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    PRIMARY KEY (game_id, user_id),
    FOREIGN KEY (game_id) REFERENCES games (game_id)
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


def upsert_game(conn, *, game_id, season_id, game_type, created_at, mode_id, mode_identifier, map_id, map_name):
    conn.execute(
        """
        INSERT INTO games (game_id, season_id, game_type, created_at, mode_id, mode_identifier, map_id, map_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_id) DO UPDATE SET
            season_id=excluded.season_id,
            game_type=excluded.game_type,
            created_at=excluded.created_at,
            mode_id=excluded.mode_id,
            mode_identifier=excluded.mode_identifier,
            map_id=excluded.map_id,
            map_name=excluded.map_name
        """,
        (game_id, season_id, game_type, created_at, mode_id, mode_identifier, map_id, map_name),
    )


def upsert_game_player(conn, *, game_id, user_id, is_mvp, outcome, kills, deaths, assists):
    conn.execute(
        """
        INSERT INTO game_players (game_id, user_id, is_mvp, outcome, kills, deaths, assists)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_id, user_id) DO UPDATE SET
            is_mvp=excluded.is_mvp,
            outcome=excluded.outcome,
            kills=excluded.kills,
            deaths=excluded.deaths,
            assists=excluded.assists
        """,
        (game_id, user_id, int(is_mvp), outcome, kills, deaths, assists),
    )
