
from fastapi import HTTPException
from psycopg.errors import UniqueViolation

from app.repositories import assignment_repository,ticket_repository

def assign_ticket(conn, ticket_id: int, assignment_data):

    try:
        result = assignment_repository.assign_ticket(
            conn=conn,
            ticket_id=ticket_id,
            staff_id=assignment_data.staff_id,
            assigned_by=assignment_data.assigned_by
        )

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Ticket already has an active assignment"
        )

    if isinstance(result, dict) and "error" in result:
        errors = {
            "TICKET_NOT_FOUND": (404, "Ticket not found"),
            "STAFF_NOT_FOUND": (404, "Active support staff member not found"),
            "ASSIGNER_NOT_FOUND": (403, "Only active support staff or admins can assign tickets"),
            "ALREADY_ASSIGNED": (409, "Ticket already has an active assignment")
        }

        code, message = errors[result["error"]]

        raise HTTPException(status_code=code, detail=message)

    return result

def reassign_ticket(
    conn,
    ticket_id: int,
    new_staff_id: int,
    reassigned_by: int
):
    try:
        result = assignment_repository.reassign_ticket(
            conn=conn,
            ticket_id=ticket_id,
            new_staff_id=new_staff_id,
            reassigned_by=reassigned_by
        )

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Ticket already has an active assignment"
        )

    if isinstance(result, dict) and "error" in result:
        errors = {
            "TICKET_NOT_FOUND": (404, "Ticket not found"),
            "INVALID_ACTOR": (403, "Only active support staff or admins can reassign tickets"),
            "NOT_ASSIGNED": (403, "You are not assigned to this ticket"),
            "STAFF_NOT_FOUND": (404, "Active support staff member not found"),
            "NO_ACTIVE_ASSIGNMENT": (409, "Ticket has no active assignment"),
            "SAME_STAFF": (409, "Ticket is already assigned to this staff member")
        }

        code, message = errors[result["error"]]

        raise HTTPException(status_code=code, detail=message)

    return result


def get_ticket_assignments(conn, ticket_id: int):

    ticket = ticket_repository.get_ticket_by_id(
        conn,
        ticket_id
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return assignment_repository.get_ticket_assignments(
        conn,
        ticket_id
    )