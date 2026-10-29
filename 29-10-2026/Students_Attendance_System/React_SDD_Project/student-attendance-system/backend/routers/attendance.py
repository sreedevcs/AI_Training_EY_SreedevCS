
from datetime import date

from fastapi import APIRouter, HTTPException, Query, Depends
from routers.dependencies import require_teacher, require_student

from database import get_db_connection

from typing import Literal
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/attendance",
    tags=["Attendance"],
)


@router.get("/")
def get_daily_attendance(
    attendance_date: date = Query(...), user=Depends(require_teacher),
):
    if attendance_date > date.today():
        raise HTTPException(
            status_code=422,
            detail="Future attendance dates are not allowed.",
        )

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        s.id AS student_id,
                        s.name,
                        s.register_number,
                        s.class_name,
                        a.id AS attendance_id,
                        a.status
                    FROM students s
                    LEFT JOIN attendance a
                        ON a.student_id = s.id
                        AND a.attendance_date = %s
                    WHERE s.is_active = TRUE
                    ORDER BY s.name;
                    """,
                    (attendance_date,),
                )

                records = cursor.fetchall()

        return {
            "attendance_date": attendance_date,
            "records": records,
        }

    except Exception as exc:
        print(f"Error retrieving daily attendance: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve daily attendance.",
        ) from exc


class AttendanceRecordInput(BaseModel):
    student_id: int = Field(gt=0)
    status: Literal["Present", "Absent"]


class BulkAttendanceInput(BaseModel):
    attendance_date: date
    records: list[AttendanceRecordInput] = Field(min_length=1)


@router.post("/bulk")
def save_bulk_attendance(payload: BulkAttendanceInput, user=Depends(require_teacher)):
    if payload.attendance_date > date.today():
        raise HTTPException(
            status_code=422,
            detail="Future attendance dates are not allowed.",
        )

    submitted_ids = [record.student_id for record in payload.records]

    if len(submitted_ids) != len(set(submitted_ids)):
        raise HTTPException(
            status_code=422,
            detail="Duplicate student IDs are not allowed.",
        )

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM students
                    WHERE is_active = TRUE
                    ORDER BY id;
                    """
                )
                active_ids = {row["id"] for row in cursor.fetchall()}
                submitted_set = set(submitted_ids)

                if submitted_set != active_ids:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            "Submit exactly one attendance status "
                            "for every active student."
                        ),
                    )

                cursor.executemany(
                    """
                    INSERT INTO attendance
                        (student_id, attendance_date, status)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (student_id, attendance_date)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    [
                        (
                            record.student_id,
                            payload.attendance_date,
                            record.status,
                        )
                        for record in payload.records
                    ],
                )

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Error saving attendance: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to save attendance.",
        ) from exc

    return {
        "message": "Attendance saved successfully.",
        "attendance_date": payload.attendance_date,
        "records_saved": len(payload.records),
    }


@router.get("/me")
def get_my_attendance(
    user=Depends(require_student),
):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name, register_number, class_name
                    FROM students
                    WHERE id = %s;
                    """,
                    (user["student_id"],),
                )
                student = cursor.fetchone()

                if student is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Linked student record not found.",
                    )

                cursor.execute(
                    """
                    SELECT
                        attendance_date,
                        status
                    FROM attendance
                    WHERE student_id = %s
                    ORDER BY attendance_date DESC;
                    """,
                    (user["student_id"],),
                )
                history = cursor.fetchall()

        present_count = sum(
            1 for record in history if record["status"] == "Present"
        )
        absent_count = sum(
            1 for record in history if record["status"] == "Absent"
        )
        recorded_count = len(history)

        percentage = (
            round(present_count * 100 / recorded_count, 1)
            if recorded_count
            else None
        )

        return {
            "student": student,
            "present_count": present_count,
            "absent_count": absent_count,
            "recorded_count": recorded_count,
            "attendance_percentage": percentage,
            "history": history,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Error retrieving personal attendance: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve personal attendance.",
        ) from exc
