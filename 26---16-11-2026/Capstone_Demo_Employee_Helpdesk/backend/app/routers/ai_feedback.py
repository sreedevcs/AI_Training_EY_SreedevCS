
from fastapi import APIRouter, Depends, Path

from app.database import get_db
from app.schemas.ai_feedback import (
    AIFeedbackCreate,
    AIFeedbackResponse
)
from app.services import ai_service


router = APIRouter(
    prefix="/ai-suggestions",
    tags=["AI Feedback"]
)


@router.post(
    "/{suggestion_id}/feedback",
    response_model=AIFeedbackResponse,
    status_code=201
)
def submit_ai_feedback(
    suggestion_id: int = Path(gt=0),
    feedback: AIFeedbackCreate = ...,
    conn=Depends(get_db)
):

    return ai_service.submit_ai_feedback(
        conn,
        suggestion_id,
        feedback.model_dump()
    )
