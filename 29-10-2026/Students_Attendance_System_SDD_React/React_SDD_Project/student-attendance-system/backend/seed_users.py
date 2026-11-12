
from database import get_db_connection
from security import hash_password


with get_db_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET is_active = FALSE
            WHERE username = %s AND role = 'Student';
            """,
            ("student",),
        )
        cursor.execute(
            """
            DELETE FROM auth_sessions
            WHERE user_id IN (
                SELECT id
                FROM users
                WHERE username = %s AND role = 'Student'
            );
            """,
            ("student",),
        )

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, 'Teacher')
            ON CONFLICT (username) DO NOTHING;
            """,
            ("teacher", hash_password("teacher123")),
        )

print("Teacher account seeded. Legacy student login deactivated if present.")
