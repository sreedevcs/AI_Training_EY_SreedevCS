
from fastapi import APIRouter, Depends
from psycopg import Connection

from app.database import get_db
from app.schemas.assignment import (
    TicketAssignmentCreate,
    TicketAssignmentResponse,
    TicketReassignmentCreate,
    TicketAssignmentHistoryResponse
)
from app.services import assignment_service


router = APIRouter(
    prefix="/tickets",
    tags=["Ticket Assignments"]
)


@router.post(
    "/{ticket_id}/assign",
    response_model=TicketAssignmentResponse,
    status_code=201
)
def assign_ticket(
    ticket_id: int,
    assignment_data: TicketAssignmentCreate,
    conn: Connection = Depends(get_db)
):
    return assignment_service.assign_ticket(
        conn,
        ticket_id,
        assignment_data
    )


@router.patch(
    "/{ticket_id}/reassign",
    response_model=TicketAssignmentResponse
)
def reassign_ticket(
    ticket_id: int,
    reassignment_data: TicketReassignmentCreate,
    conn: Connection = Depends(get_db)
):
    return assignment_service.reassign_ticket(
        conn=conn,
        ticket_id=ticket_id,
        new_staff_id=reassignment_data.new_staff_id,
        reassigned_by=reassignment_data.reassigned_by
    )


@router.get(
    "/{ticket_id}/assignments",
    response_model=list[TicketAssignmentHistoryResponse]
)
def get_ticket_assignments(
    ticket_id: int,
    conn: Connection = Depends(get_db)
):
    return assignment_service.get_ticket_assignments(
        conn,
        ticket_id
    )
