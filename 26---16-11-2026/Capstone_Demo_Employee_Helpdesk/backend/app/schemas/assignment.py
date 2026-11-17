
from datetime import datetime

from pydantic import BaseModel, Field


class TicketAssignmentCreate(BaseModel):
    staff_id: int = Field(gt=0)
    assigned_by: int = Field(gt=0)


class TicketAssignmentResponse(BaseModel):
    assignment_id: int
    ticket_id: int
    staff_id: int
    assigned_by: int | None
    assigned_at: datetime
    unassigned_at: datetime | None
    assignment_status: str

class TicketReassignmentCreate(BaseModel):
    new_staff_id: int = Field(gt=0)
    reassigned_by: int = Field(gt=0)

class TicketAssignmentHistoryResponse(BaseModel):
    assignment_id: int
    ticket_id: int
    staff_id: int
    assigned_by: int | None
    assigned_at: datetime
    unassigned_at: datetime | None
    assignment_status: str
    staff_name: str
    staff_email: str