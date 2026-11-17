
from fastapi import APIRouter, Depends

from app.database import get_db
from app.services import ai_service
from app.schemas.ai_feedback import AISuggestionHistoryResponse


router = APIRouter(
    prefix="/tickets",
    tags=["AI Analysis"]
)


@router.post("/{ticket_id}/analyze")
def analyze_ticket(ticket_id: int, conn=Depends(get_db)):

    return ai_service.analyze_ticket(
        conn,
        ticket_id
    )



@router.get(
    "/{ticket_id}/ai-suggestions",
    response_model=list[AISuggestionHistoryResponse]
)
def get_ticket_ai_suggestions(
    ticket_id: int,
    conn=Depends(get_db)
):

    return ai_service.get_ticket_ai_suggestions(
        conn,
        ticket_id
    )
