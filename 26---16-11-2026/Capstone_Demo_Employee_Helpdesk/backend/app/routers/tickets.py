
from fastapi import APIRouter, Depends, Query, status
from psycopg import Connection

from app.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate,TicketHistoryResponse,TicketStatusUpdate, TicketPriorityUpdate
from app.services import ticket_service
from app.schemas.ticket import TicketCommentCreate,TicketCommentResponse


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    ticket_data: TicketCreate,
    conn: Connection = Depends(get_db)
):
    return ticket_service.create_ticket(conn, ticket_data)


@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_all_tickets(
    conn: Connection = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
    category: str | None = None,
    priority: str | None = None,
    requester_id: int | None = None,
    limit: int = Query(default=100, ge=1),
    offset: int = Query(default=0, ge=0)
):
    return ticket_service.get_all_tickets(
        conn=conn,
        status=status_filter,
        category=category,
        priority=priority,
        requester_id=requester_id,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse]
)
def get_ticket_history(
    ticket_id: int,
    conn: Connection = Depends(get_db)
):
    return ticket_service.get_ticket_history(
        conn,
        ticket_id
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_by_id(
    ticket_id: int,
    conn: Connection = Depends(get_db)
):
    return ticket_service.get_ticket_by_id(
        conn,
        ticket_id
    )


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    conn: Connection = Depends(get_db)
):
    update_data = ticket_data.model_dump(exclude_unset=True)

    return ticket_service.update_ticket(
        conn,
        ticket_id,
        update_data
    )


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    conn: Connection = Depends(get_db)
):
    return ticket_service.update_ticket_status(
        conn=conn,
        ticket_id=ticket_id,
        status=status_data.status,
        updated_by=status_data.updated_by
    )


@router.patch(
    "/{ticket_id}/priority",
    response_model=TicketResponse
)
def update_ticket_priority(
    ticket_id: int,
    priority_data: TicketPriorityUpdate,
    conn: Connection = Depends(get_db)
):
    return ticket_service.update_ticket_priority(
        conn=conn,
        ticket_id=ticket_id,
        priority=priority_data.priority,
        updated_by=priority_data.updated_by
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=201
)
def add_ticket_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    conn: Connection = Depends(get_db)
):
    return ticket_service.add_ticket_comment(
        conn=conn,
        ticket_id=ticket_id,
        comment=comment_data.comment,
        added_by=comment_data.added_by
    )


