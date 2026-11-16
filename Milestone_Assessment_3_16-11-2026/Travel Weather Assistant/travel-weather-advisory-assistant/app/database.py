import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATABASE_PATH = os.getenv("DATABASE_PATH", "trips.db")

if not Path(DATABASE_PATH).is_absolute():
    DATABASE_PATH = str(ROOT_DIR / DATABASE_PATH)


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            purpose TEXT NOT NULL,
            status TEXT DEFAULT 'Planned'
        )
    """)

    conn.commit()
    conn.close()


def create_trip(employee_id, destination, start_date,
                end_date, purpose):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trips (
            employee_id, destination, start_date,
            end_date, purpose
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        employee_id,
        destination,
        start_date,
        end_date,
        purpose
    ))

    trip_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return get_trip_by_id(trip_id)


def get_trip_by_id(trip_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM trips WHERE id = ?",
        (trip_id,)
    )

    trip = cursor.fetchone()
    conn.close()

    return dict(trip) if trip else None

def get_trips_by_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM trips WHERE employee_id = ?",
        (employee_id,)
    )

    trips = cursor.fetchall()
    conn.close()

    return [dict(trip) for trip in trips]