
from fastapi import Depends, HTTPException

from routers.auth import get_current_user


def require_teacher(user=Depends(get_current_user)):
    if user["role"] != "Teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher access required.",
        )
    return user


def require_student(user=Depends(get_current_user)):
    if user["role"] != "Student":
        raise HTTPException(
            status_code=403,
            detail="Student access required.",
        )
    if user["student_id"] is None:
        raise HTTPException(
            status_code=403,
            detail="Student account is not linked to a student record.",
        )
    return user
