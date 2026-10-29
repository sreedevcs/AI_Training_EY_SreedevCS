
import re

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from psycopg.errors import UniqueViolation

from database import get_db_connection
from routers.dependencies import require_teacher
from security import hash_password

router = APIRouter(
    prefix="/api/v1/students",
    tags=["Students"],
)


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    register_number: str = Field(min_length=1, max_length=30)
    class_name: str = Field(min_length=1, max_length=50)


def normalize_student(student: StudentCreate):
    name = student.name.strip()
    register_number = student.register_number.strip()
    class_name = student.class_name.strip()

    if not 2 <= len(name) <= 100:
        raise HTTPException(
            status_code=422,
            detail="Name must contain 2–100 characters.",
        )

    if not register_number or len(register_number) > 30:
        raise HTTPException(
            status_code=422,
            detail="Register number must contain 1–30 characters.",
        )

    if not class_name or len(class_name) > 50:
        raise HTTPException(
            status_code=422,
            detail="Class/section must contain 1–50 characters.",
        )

    return name, register_number, class_name


def create_student_account(cursor, name, student_id):
    base_username = re.sub(r"[^a-z0-9]", "", name.lower()) or "student"
    suffix = 1

    while True:
        suffix_text = "" if suffix == 1 else str(suffix)
        username = (
            f"{base_username[:100 - len(suffix_text)]}{suffix_text}"
        )
        password = f"{username}123"

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, student_id)
            VALUES (%s, %s, 'Student', %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING username;
            """,
            (username, hash_password(password), student_id),
        )
        created_account = cursor.fetchone()

        if created_account:
            return {
                "username": username,
                "password": password,
            }

        suffix += 1


@router.get("/")
def get_students(user=Depends(require_teacher)):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, register_number,
                           class_name, is_active, is_deleted
                    FROM students
                    ORDER BY name;
                    """
                )
                return {"students": cursor.fetchall()}

    except Exception as exc:
        print(f"Error retrieving students: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve students.",
        ) from exc


@router.post("/", status_code=201)
def create_student(student: StudentCreate, user=Depends(require_teacher)):
    name, register_number, class_name = normalize_student(student)

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO students
                        (name, register_number, class_name)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, register_number,
                              class_name, is_active, is_deleted;
                    """,
                    (name, register_number, class_name),
                )
                created_student = cursor.fetchone()
                credentials = create_student_account(
                    cursor, name, created_student["id"]
                )

        return {
            "student": created_student,
            "credentials": credentials,
        }

    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="A student with this register number already exists.",
        ) from exc

    except Exception as exc:
        print(f"Error creating student: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to create student.",
        ) from exc


from typing import Optional

from pydantic import ConfigDict


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    register_number: Optional[str] = Field(
        default=None, min_length=1, max_length=30
    )
    class_name: Optional[str] = Field(
        default=None, min_length=1, max_length=50
    )
    is_active: Optional[bool] = None


@router.patch("/{student_id}")
def update_student(student_id: int, student: StudentUpdate, user=Depends(require_teacher)):
    changes = student.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    allowed_fields = {
        "name",
        "register_number",
        "class_name",
        "is_active",
    }

    for field in changes:
        if field not in allowed_fields:
            raise HTTPException(status_code=400, detail="Invalid field.")

    for field in ("name", "register_number", "class_name"):
        if field in changes:
            value = changes[field]
            if value is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} cannot be null.",
                )
            changes[field] = value.strip()

    if "name" in changes and not 2 <= len(changes["name"]) <= 100:
        raise HTTPException(status_code=422, detail="Invalid name length.")

    if "register_number" in changes and not 1 <= len(
        changes["register_number"]
    ) <= 30:
        raise HTTPException(
            status_code=422,
            detail="Invalid register number length.",
        )

    if "class_name" in changes and not 1 <= len(
        changes["class_name"]
    ) <= 50:
        raise HTTPException(status_code=422, detail="Invalid class name.")

    columns = list(changes)
    assignments = ", ".join(f"{column} = %s" for column in columns)
    values = [changes[column] for column in columns]

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE students
                    SET {assignments}
                    WHERE id = %s
                      AND is_deleted = FALSE
                    RETURNING id, name, register_number,
                              class_name, is_active, is_deleted;
                    """,
                    (*values, student_id),
                )

                updated_student = cursor.fetchone()

                if updated_student is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Student not found or has been deleted.",
                    )

                if "is_active" in changes:
                    cursor.execute(
                        """
                        UPDATE users
                        SET is_active = %s
                        WHERE student_id = %s AND role = 'Student';
                        """,
                        (changes["is_active"], student_id),
                    )

                    if not changes["is_active"]:
                        cursor.execute(
                            """
                            DELETE FROM auth_sessions
                            WHERE user_id IN (
                                SELECT id
                                FROM users
                                WHERE student_id = %s AND role = 'Student'
                            );
                            """,
                            (student_id,),
                        )

        return {"student": updated_student}

    except HTTPException:
        raise

    except Exception as exc:
        from psycopg.errors import UniqueViolation

        if isinstance(exc, UniqueViolation):
            raise HTTPException(
                status_code=409,
                detail="A student with this register number already exists.",
            ) from exc

        print(f"Error updating student: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to update student.",
        ) from exc


@router.delete("/{student_id}")
def delete_student(student_id: int, user=Depends(require_teacher)):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE students
                    SET is_active = FALSE,
                        is_deleted = TRUE
                    WHERE id = %s
                      AND is_deleted = FALSE
                    RETURNING id;
                    """,
                    (student_id,),
                )

                if cursor.fetchone() is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Student not found or has already been deleted.",
                    )

                cursor.execute(
                    """
                    UPDATE users
                    SET is_active = FALSE
                    WHERE student_id = %s AND role = 'Student';
                    """,
                    (student_id,),
                )
                cursor.execute(
                    """
                    DELETE FROM auth_sessions
                    WHERE user_id IN (
                        SELECT id
                        FROM users
                        WHERE student_id = %s AND role = 'Student'
                    );
                    """,
                    (student_id,),
                )

        return {
            "message": "Student deleted and linked login deactivated."
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Error deleting student: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete student.",
        ) from exc
