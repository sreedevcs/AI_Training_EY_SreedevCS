
from fastapi import HTTPException

from app.repositories import ticket_repository
from app.schemas.ticket import TicketCreate


def create_ticket(conn, ticket_data: TicketCreate):
    ticket = ticket_repository.create_ticket(
        conn,
        ticket_data.model_dump()
    )

    if ticket is None:
        raise HTTPException(
            status_code=400,
            detail="Requester does not exist, is inactive, or is not an employee"
        )

    return ticket



def get_all_tickets(
    conn,
    status=None,
    category=None,
    priority=None,
    requester_id=None,
    limit=100,
    offset=0
):
    return ticket_repository.get_all_tickets(
        conn=conn,
        status=status,
        category=category,
        priority=priority,
        requester_id=requester_id,
        limit=limit,
        offset=offset
    )


from fastapi import HTTPException


def get_ticket_by_id(conn, ticket_id: int):
    ticket = ticket_repository.get_ticket_by_id(
        conn,
        ticket_id
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    return ticket


from fastapi import HTTPException
from app.repositories import ticket_repository


def update_ticket(conn, ticket_id: int, update_data: dict):

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided"
        )

    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=422,
            detail="Fields cannot be explicitly set to null"
        )

    ticket = ticket_repository.update_ticket(
        conn,
        ticket_id,
        update_data
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    return ticket


from fastapi import HTTPException
from app.repositories import ticket_repository


def get_ticket_history(conn, ticket_id: int):
    # First verify that the ticket exists
    ticket = ticket_repository.get_ticket_by_id(
        conn,
        ticket_id
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    return ticket_repository.get_ticket_history(
        conn,
        ticket_id
    )

def update_ticket_status(
    conn,
    ticket_id: int,
    status: str,
    updated_by: int
):
    result = ticket_repository.update_ticket_status(
        conn=conn,
        ticket_id=ticket_id,
        new_status=status,
        updated_by=updated_by
    )

    if isinstance(result, dict) and "error" in result:

        error = result["error"]

        if error == "TICKET_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail=f"Ticket with ID {ticket_id} not found"
            )

        if error == "INVALID_ACTOR":
            raise HTTPException(
                status_code=403,
                detail="Only active support staff or admins can update ticket status"
            )

        if error == "NOT_ASSIGNED":
            raise HTTPException(
                status_code=403,
                detail="Support staff member is not assigned to this ticket"
            )

        if error == "INVALID_TRANSITION":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot change status from "
                    f"{result['current_status']} to "
                    f"{result['requested_status']}"
                )
            )

    return result


from fastapi import HTTPException
from app.repositories import ticket_repository


def update_ticket_priority(
    conn,
    ticket_id: int,
    priority: str,
    updated_by: int
):
    result = ticket_repository.update_ticket_priority(
        conn=conn,
        ticket_id=ticket_id,
        new_priority=priority,
        updated_by=updated_by
    )

    if isinstance(result, dict) and "error" in result:
        error = result["error"]

        if error == "TICKET_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail=f"Ticket with ID {ticket_id} not found"
            )

        if error == "INVALID_ACTOR":
            raise HTTPException(
                status_code=403,
                detail="Only active support staff or admins can update priority"
            )

        if error == "NOT_ASSIGNED":
            raise HTTPException(
                status_code=403,
                detail="Support staff member is not assigned to this ticket"
            )

        if error == "SAME_PRIORITY":
            raise HTTPException(
                status_code=409,
                detail="Ticket already has this priority"
            )

    return result

def add_ticket_comment(
    conn,
    ticket_id: int,
    comment: str,
    added_by: int
):
    result = ticket_repository.add_ticket_comment(
        conn=conn,
        ticket_id=ticket_id,
        comment=comment,
        added_by=added_by
    )

    if isinstance(result, dict) and "error" in result:
        error = result["error"]

        if error == "TICKET_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        if error == "USER_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail="Active user not found"
            )

        if error == "NOT_ASSIGNED":
            raise HTTPException(
                status_code=403,
                detail="Support staff member is not assigned to this ticket"
            )

        if error == "NOT_AUTHORIZED":
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to comment on this ticket"
            )

    return result
