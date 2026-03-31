import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "weather_forecast.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_date TEXT NOT NULL,
    base_time TEXT NOT NULL,
    fcst_date TEXT NOT NULL,
    fcst_time TEXT NOT NULL,
    forecast_datetime TEXT NOT NULL,
    category TEXT NOT NULL,
    fcst_value TEXT,
    nx INTEGER NOT NULL,
    ny INTEGER NOT NULL,
    location_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_date, base_time, fcst_date, fcst_time, category, nx, ny)
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    os.makedirs(BASE_DIR, exist_ok=True)
    with get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
