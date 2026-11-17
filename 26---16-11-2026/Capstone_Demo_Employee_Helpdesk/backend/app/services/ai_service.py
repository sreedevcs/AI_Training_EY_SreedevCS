
import json

from fastapi import HTTPException
from pydantic import ValidationError

from app.ai.huggingface_client import get_llm
from app.ai.prompts import format_ticket_analysis_prompt
from app.repositories import ai_repository, ticket_repository
from app.schemas.ai_suggestion import AIAnalysisResponse
from app.ai.huggingface_client import MODEL_NAME
from app.schemas.ai_feedback import AIFeedbackResponse


def analyze_ticket(conn, ticket_id: int):

    # 1. Fetch the requested ticket
    ticket = ticket_repository.get_ticket_by_id(
        conn,
        ticket_id
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # 2. Fetch recent historical tickets
    history = ai_repository.get_recent_tickets(
        conn,
        exclude_ticket_id=ticket_id,
        limit=20
    )

    # 3. Convert historical records into JSON
    history_data = json.dumps(
        history,
        indent=2,
        default=str
    )

    try:
        # 4. Prepare the prompt
        prompt_value = format_ticket_analysis_prompt(
            ticket_id=ticket["ticket_id"],
            title=ticket["title"],
            description=ticket["description"],
            current_category=ticket["category"],
            current_priority=ticket["priority"],
            history=history_data
        )

        # 5. Invoke the local Hugging Face model
        llm = get_llm()

        raw_response = llm.invoke(prompt_value.to_string())

        # 6. Extract the first complete JSON object from the model response
        decoder = json.JSONDecoder()
        response_data = None
        start = 0

        while True:
            start = raw_response.find("{", start)
            if start == -1:
                break

            try:
                response_data, _ = decoder.raw_decode(raw_response, start)
            except json.JSONDecodeError:
                start += 1
                continue

            if isinstance(response_data, dict):
                break

            response_data = None
            start += 1

        if response_data is None:
            raise ValueError("AI response does not contain a valid JSON object")

        # 7. Validate using Pydantic
        validated_response = AIAnalysisResponse(
            **response_data
        )

        # 8. Save the AI suggestion in PostgreSQL
        saved_suggestion = ai_repository.save_ai_suggestion(
            conn,
            ticket_id,
            validated_response.model_dump(),
            MODEL_NAME
        )

        return {
            "suggestion_id": saved_suggestion["suggestion_id"],
            "ticket_id": ticket_id,
            "created_at": saved_suggestion["created_at"],
            "analysis": validated_response.model_dump()
        }

    except (json.JSONDecodeError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid AI response: {str(exc)}"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI model unavailable or analysis failed: {str(exc)}"
        )


def submit_ai_feedback(conn, suggestion_id: int, feedback: dict):

    # 1. Check whether the AI suggestion exists
    suggestion = ai_repository.get_ai_suggestion_by_id(
        conn,
        suggestion_id
    )

    if suggestion is None:
        raise HTTPException(
            status_code=404,
            detail="AI suggestion not found"
        )

    # 2. Validate the support staff member
    staff = ai_repository.get_active_support_staff(
        conn,
        feedback["reviewed_by"]
    )

    if staff is None:
        raise HTTPException(
            status_code=403,
            detail="Invalid or inactive support staff"
        )

    # 3. Save feedback
    if feedback["decision"] == "ACCEPTED":
        final_category = suggestion["suggested_category"]
        final_priority = suggestion["suggested_priority"]
    elif feedback["decision"] == "CORRECTED":
        final_category = (
            feedback.get("corrected_category")
            or suggestion["suggested_category"]
        )
        final_priority = (
            feedback.get("corrected_priority")
            or suggestion["suggested_priority"]
        )
    else:
        final_category = None
        final_priority = None

    saved_feedback = ai_repository.save_ai_feedback(
        conn,
        suggestion_id,
        feedback,
        final_category,
        final_priority
    )

    # 4. Validate the response structure
    return AIFeedbackResponse(**saved_feedback)



def get_ticket_ai_suggestions(conn, ticket_id: int):

    # 1. Verify that the ticket exists
    ticket = ticket_repository.get_ticket_by_id(
        conn,
        ticket_id
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # 2. Retrieve all AI suggestions
    suggestions = ai_repository.get_ai_suggestions_by_ticket(
        conn,
        ticket_id
    )

    # 3. Retrieve feedback for those suggestions
    suggestion_ids = [
        item["suggestion_id"]
        for item in suggestions
    ]

    feedback_records = ai_repository.get_feedback_by_suggestion_ids(
        conn,
        suggestion_ids
    )

    # 4. Group feedback by suggestion ID
    feedback_map = {}

    for feedback in feedback_records:
        suggestion_id = feedback["suggestion_id"]

        feedback_map.setdefault(
            suggestion_id,
            []
        ).append(feedback)

    # 5. Attach feedback to each suggestion
    result = []

    for suggestion in suggestions:

        suggestion_data = dict(suggestion)

        suggestion_data["feedback"] = feedback_map.get(
            suggestion["suggestion_id"],
            []
        )

        result.append(
            suggestion_data
        )

    return result
