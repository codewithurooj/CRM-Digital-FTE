"""Ticket status endpoint — GET /api/v1/tickets/{ticket_id}."""
from fastapi import APIRouter, Depends, HTTPException

from production.api.dependencies import get_db_pool
from production.schemas.tickets import TicketResponse, TicketResponseEntry
from production.database.queries import tickets as ticket_queries
from production.database.queries import messages as message_queries

router = APIRouter()


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket_status(
    ticket_id: str,
    pool=Depends(get_db_pool),
):
    """Get ticket status by ticket number (TKT-XXXX)."""
    ticket = await ticket_queries.get_ticket_by_number(pool, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get agent responses for this ticket's conversation
    responses = []
    if ticket.get("conversation_id"):
        msgs = await message_queries.get_messages_by_conversation(
            pool, ticket["conversation_id"],
        )
        responses = [
            TicketResponseEntry(
                content=m["content"],
                channel=m["channel"],
                created_at=m["created_at"],
            )
            for m in msgs
            if m.get("direction") == "outbound" and m.get("role") == "agent"
        ]

    return TicketResponse(
        ticket_id=ticket["ticket_number"],
        status=ticket["status"],
        category=ticket["category"],
        priority=ticket["priority"],
        subject=ticket["subject"],
        source_channel=ticket["source_channel"],
        created_at=ticket["created_at"],
        updated_at=ticket["updated_at"],
        resolved_at=ticket.get("resolved_at"),
        responses=responses,
    )
