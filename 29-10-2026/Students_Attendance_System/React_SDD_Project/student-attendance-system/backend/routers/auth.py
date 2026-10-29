
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from database import get_db_connection
from security import (
    create_token,
    hash_token,
    verify_password,
    token_expiry,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.username, u.role, u.student_id
                    FROM auth_sessions s
                    JOIN users u ON u.id = s.user_id
                    WHERE s.token_hash = %s
                      AND s.expires_at > CURRENT_TIMESTAMP
                      AND u.is_active = TRUE;
                    """,
                    (hash_token(credentials.credentials),),
                )
                user = cursor.fetchone()
    except Exception as exc:
        print(f"Authentication lookup failed: {exc}")
        raise HTTPException(
            status_code=503, detail="Authentication service unavailable."
        ) from exc

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return user


@router.post("/login")
def login(payload: LoginRequest):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash, role, student_id
                FROM users
                WHERE username = %s AND is_active = TRUE;
                """,
                (payload.username.strip(),),
            )
            user = cursor.fetchone()

            if not user or not verify_password(
                payload.password, user["password_hash"]
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password.",
                )

            token = create_token()
            cursor.execute(
                """
                INSERT INTO auth_sessions (user_id, token_hash, expires_at)
                VALUES (%s, %s, %s);
                """,
                (user["id"], hash_token(token), token_expiry()),
            )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "student_id": user["student_id"],
        },
    }


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "student_id": user["student_id"],
    }


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM auth_sessions WHERE token_hash = %s;",
                (hash_token(credentials.credentials),),
            )

    return {"message": "Logged out successfully."}
