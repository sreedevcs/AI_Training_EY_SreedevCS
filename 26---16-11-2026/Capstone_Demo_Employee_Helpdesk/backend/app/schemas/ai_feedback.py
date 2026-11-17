
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AIFeedbackCreate(BaseModel):

    reviewed_by: int = Field(gt=0)

    is_useful: bool

    decision: Literal["ACCEPTED", "CORRECTED", "REJECTED"] | None = None

    corrected_category: Literal[
        "HARDWARE",
        "SOFTWARE",
        "NETWORK",
        "ACCESS",
        "OTHER"
    ] | None = None

    corrected_priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ] | None = None

    comments: str | None = Field(
        default=None,
        max_length=1000
    )

    @model_validator(mode="after")
    def validate_feedback(self):

        if self.comments is not None:
            self.comments = self.comments.strip()

            if not self.comments:
                self.comments = None

        has_correction = (
            self.corrected_category is not None
            or self.corrected_priority is not None
        )

        if self.decision is None:
            if has_correction:
                self.decision = "CORRECTED"
            elif self.is_useful:
                self.decision = "ACCEPTED"
            else:
                self.decision = "REJECTED"

        if self.decision == "CORRECTED" and not has_correction:
            raise ValueError(
                "At least one corrected value is required for a CORRECTED decision"
            )

        if self.decision != "CORRECTED" and has_correction:
            raise ValueError(
                "Corrected values can only be provided for a CORRECTED decision"
            )

        return self


class AIFeedbackResponse(BaseModel):

    feedback_id: int
    suggestion_id: int
    reviewed_by: int
    is_useful: bool
    decision: Literal["ACCEPTED", "CORRECTED", "REJECTED"]
    corrected_category: str | None
    corrected_priority: str | None
    final_category: str | None
    final_priority: str | None
    comments: str | None


class AIFeedbackHistoryResponse(BaseModel):
    feedback_id: int
    reviewed_by: int
    is_useful: bool
    decision: Literal["ACCEPTED", "CORRECTED", "REJECTED"]
    corrected_category: str | None
    corrected_priority: str | None
    final_category: str | None
    final_priority: str | None
    comments: str | None


class AISuggestionHistoryResponse(BaseModel):
    suggestion_id: int
    ticket_id: int
    suggested_category: str
    suggested_priority: str
    troubleshooting_steps: str
    explanation: str
    model_name: str
    created_at: datetime
    feedback: list[AIFeedbackHistoryResponse] = Field(
        default_factory=list
    )
