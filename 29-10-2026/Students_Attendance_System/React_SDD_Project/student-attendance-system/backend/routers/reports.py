
from fastapi import APIRouter, HTTPException, Depends

from database import get_db_connection

from routers.dependencies import require_teacher

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
)


@router.get("/attendance")
def attendance_report(user=Depends(require_teacher)):
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
                        COUNT(a.id) FILTER (
                            WHERE a.status = 'Present'
                        ) AS present_count,
                        COUNT(a.id) FILTER (
                            WHERE a.status = 'Absent'
                        ) AS absent_count,
                        COUNT(a.id) AS recorded_count,
                        ROUND(
                            100.0 * COUNT(a.id) FILTER (
                                WHERE a.status = 'Present'
                            ) / NULLIF(COUNT(a.id), 0),
                            1
                        ) AS attendance_percentage
                    FROM students s
                    LEFT JOIN attendance a
                        ON a.student_id = s.id
                    GROUP BY s.id
                    ORDER BY s.name;
                    """
                )

                rows = cursor.fetchall()

        for row in rows:
            if row["attendance_percentage"] is None:
                row["attendance_percentage"] = "N/A"

        return {"reports": rows}

    except Exception as exc:
        print(f"Error generating attendance report: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate attendance report.",
        ) from exc
