
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


TicketCategory = Literal[
    "HARDWARE",
    "SOFTWARE",
    "NETWORK",
    "ACCESS",
    "OTHER"
]


class TicketCreate(BaseModel):
    requester_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    category: TicketCategory = "OTHER"

    @field_validator("title", "description")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class TicketResponse(BaseModel):
    ticket_id: int
    requester_id: int
    requester_name: str | None = None
    requester_email: str | None = None
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


from pydantic import BaseModel, Field, field_validator
from typing import Literal


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    category: Literal[
        "HARDWARE",
        "SOFTWARE",
        "NETWORK",
        "ACCESS",
        "OTHER"
    ] | None = None

    @field_validator("title", "description")
    @classmethod
    def validate_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


from datetime import datetime
from pydantic import BaseModel


class TicketHistoryResponse(BaseModel):
    activity_id: int
    ticket_id: int
    performed_by: int | None
    activity_type: str
    comment: str | None
    old_status: str | None
    new_status: str | None
    old_priority: str | None
    new_priority: str | None
    created_at: datetime


from pydantic import BaseModel, Field
from typing import Literal


class TicketStatusUpdate(BaseModel):
    status: Literal[
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED"
    ]

    updated_by: int = Field(gt=0)

class TicketPriorityUpdate(BaseModel):
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    updated_by: int = Field(gt=0)

class TicketCommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=2000)
    added_by: int = Field(gt=0)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Comment cannot be empty")

        return value


from datetime import datetime


class TicketCommentResponse(BaseModel):
    activity_id: int
    ticket_id: int
    performed_by: int | None
    activity_type: str
    comment: str | None
    old_status: str | None
    new_status: str | None
    old_priority: str | None
    new_priority: str | None
    created_at: datetime
