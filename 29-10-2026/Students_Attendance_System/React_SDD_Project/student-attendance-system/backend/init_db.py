
from database import get_db_connection


CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
        CHECK (char_length(trim(name)) BETWEEN 2 AND 100),
    register_number VARCHAR(30) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_students_register_number
        UNIQUE (register_number)
);

ALTER TABLE students
    ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

CREATE UNIQUE INDEX IF NOT EXISTS
    uq_students_register_number_lower
ON students (LOWER(register_number));

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(10) NOT NULL
        CHECK (role IN ('Student', 'Teacher')),
    student_id INTEGER UNIQUE REFERENCES students(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (
        (role = 'Student' AND student_id IS NOT NULL)
        OR
        (role = 'Teacher' AND student_id IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    attendance_date DATE NOT NULL
        CHECK (attendance_date <= CURRENT_DATE),
    status VARCHAR(10) NOT NULL
        CHECK (status IN ('Present', 'Absent')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_attendance_student_date
        UNIQUE (student_id, attendance_date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_date
    ON attendance (attendance_date);

CREATE INDEX IF NOT EXISTS idx_attendance_student
    ON attendance (student_id);


CREATE TABLE IF NOT EXISTS auth_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

"""


def initialize_database():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLES_SQL)

    print("Database tables created successfully!")


def migrate_schema():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                ALTER TABLE students
                ADD COLUMN IF NOT EXISTS is_deleted
                    BOOLEAN NOT NULL DEFAULT FALSE;
                """
            )


if __name__ == "__main__":
    initialize_database()
