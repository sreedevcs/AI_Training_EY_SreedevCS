
from database import get_db_connection


def test_connection():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print("Connected to PostgreSQL successfully!")
            print(result["version"])


if __name__ == "__main__":
    test_connection()
