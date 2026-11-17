
from typing import Literal

from pydantic import BaseModel, Field


class AIAnalysisResponse(BaseModel):

    suggested_category: Literal[
        "HARDWARE",
        "SOFTWARE",
        "NETWORK",
        "ACCESS",
        "OTHER"
    ]

    suggested_priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    troubleshooting_steps: str = Field(
        min_length=1,
        description="Troubleshooting instructions for the employee"
    )

    explanation: str = Field(
        min_length=1,
        description="Reasoning behind the AI recommendations"
    )
