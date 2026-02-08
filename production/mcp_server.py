"""Standalone MCP server exposing 5 CRM agent tools (FR-046).

Run: python -m production.mcp_server
"""
import json
import logging
import time

from mcp.server.fastmcp import FastMCP

from production.agent.formatters import format_response
from production.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

mcp = FastMCP(
    name="CRM Digital FTE",
    json_response=True,
    host=settings.MCP_HOST if hasattr(settings, "MCP_HOST") else "127.0.0.1",
    port=settings.MCP_PORT if hasattr(settings, "MCP_PORT") else 8090,
)


# ---------------------------------------------------------------------------
# Tool implementations (standalone functions for testability)
# ---------------------------------------------------------------------------


async def mcp_search_knowledge_base(query: str, category: str = "") -> str:
    """Search TechCorp product documentation."""
    from production.database.pool import get_pool
    from production.database.queries import knowledge_base

    pool = await get_pool()

    if category:
        results = await knowledge_base.get_by_category(pool, category)
        if results:
            entries = [
                {"title": r.get("title", ""), "content": r.get("content", "")[:500], "category": r.get("category", "")}
                for r in results[:5]
            ]
            return json.dumps({"results": entries, "total": len(entries)})

    # Fallback search
    try:
        results = await knowledge_base.get_by_category(pool, "general")
        if not results:
            for cat in ["account", "technical", "billing", "how_to", "troubleshooting"]:
                results = await knowledge_base.get_by_category(pool, cat)
                if results:
                    break
    except Exception:
        results = []

    if not results:
        return json.dumps({"results": [], "total": 0, "message": "No results found"})

    entries = [
        {"title": r.get("title", ""), "content": r.get("content", "")[:500], "category": r.get("category", "")}
        for r in results[:5]
    ]
    return json.dumps({"results": entries, "total": len(entries)})


async def mcp_create_ticket(
    customer_id: str,
    subject: str,
    category: str,
    source_channel: str,
    priority: str = "medium",
    conversation_id: str = "",
) -> str:
    """Create a support ticket for the customer."""
    from production.database.pool import get_pool
    from production.database.queries import tickets

    pool = await get_pool()
    ticket = await tickets.create_ticket(
        pool,
        customer_id=customer_id,
        subject=subject,
        category=category,
        source_channel=source_channel,
        priority=priority,
        conversation_id=conversation_id or None,
    )

    if not ticket:
        return json.dumps({"error": "Failed to create ticket"})

    return json.dumps({
        "ticket_number": ticket["ticket_number"],
        "ticket_id": str(ticket["id"]),
        "status": ticket["status"],
    })


async def mcp_get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Retrieve the customer's interaction history across all channels."""
    from production.database.pool import get_pool
    from production.database.queries import messages

    pool = await get_pool()
    history = await messages.get_customer_history(pool, customer_id, limit=limit)

    if not history:
        return json.dumps({"messages": [], "total": 0})

    formatted = [
        {
            "channel": msg.get("channel", "unknown"),
            "direction": msg.get("direction", "unknown"),
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", "")[:200],
            "created_at": str(msg.get("created_at", "")),
        }
        for msg in history
    ]
    return json.dumps({"messages": formatted, "total": len(formatted)})


async def mcp_escalate_to_human(
    customer_id: str,
    ticket_id: str,
    reason: str,
    conversation_id: str = "",
    notes: str = "",
) -> str:
    """Escalate the conversation to a human support agent."""
    from production.database.pool import get_pool
    from production.database.queries import tickets as ticket_queries
    from production.database.queries import conversations, metrics

    pool = await get_pool()

    await ticket_queries.update_ticket_status(
        pool, ticket_id, "escalated",
        escalation_reason=reason,
        resolution_notes=notes,
    )

    if conversation_id:
        await conversations.update_status(
            pool, conversation_id, "escalated",
            escalation_reason=reason,
        )

    await metrics.record_metric(
        pool, "escalation", 1.0,
        metadata={"reason": reason, "customer_id": customer_id},
    )

    return json.dumps({
        "status": "escalated",
        "reason": reason,
        "message": f"Conversation escalated to human support. Reason: {reason}",
    })


async def mcp_send_response(
    customer_id: str,
    conversation_id: str,
    channel: str,
    response_text: str,
    ticket_number: str = "",
    customer_name: str = "",
) -> str:
    """Format and send a response to the customer via their channel."""
    from production.database.pool import get_pool
    from production.database.queries import messages, metrics

    pool = await get_pool()
    start_time = time.time()

    formatted = format_response(
        response_text,
        channel=channel,
        customer_name=customer_name or "there",
        ticket_number=ticket_number,
    )

    await messages.store_message(
        pool,
        conversation_id=conversation_id,
        customer_id=customer_id,
        channel=channel,
        direction="outbound",
        role="agent",
        content=formatted,
        metadata={"ticket_number": ticket_number},
    )

    latency_ms = (time.time() - start_time) * 1000
    await metrics.record_metric(pool, "response_latency", latency_ms, channel=channel)

    return json.dumps({
        "status": "sent",
        "channel": channel,
        "formatted_length": len(formatted),
    })


# ---------------------------------------------------------------------------
# Register tools on the MCP server (thin wrappers delegating to functions above)
# ---------------------------------------------------------------------------


@mcp.tool()
async def search_knowledge_base(query: str, category: str = "") -> str:
    """Search TechCorp product documentation using semantic search.

    Args:
        query: The customer's question or search terms
        category: Optional category filter (e.g., 'account', 'billing', 'technical')
    """
    return await mcp_search_knowledge_base(query=query, category=category)


@mcp.tool()
async def create_ticket(
    customer_id: str,
    subject: str,
    category: str,
    source_channel: str,
    priority: str = "medium",
    conversation_id: str = "",
) -> str:
    """Create a support ticket for the customer. ALWAYS call this first before any response.

    Args:
        customer_id: UUID of the customer
        subject: Brief description of the issue
        category: One of: account_access, billing, technical, how_to, feature_request, complaint
        source_channel: One of: email, whatsapp, web_form
        priority: One of: low, medium, high
        conversation_id: UUID of the active conversation
    """
    return await mcp_create_ticket(
        customer_id=customer_id, subject=subject, category=category,
        source_channel=source_channel, priority=priority, conversation_id=conversation_id,
    )


@mcp.tool()
async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Retrieve the customer's interaction history across all channels.

    Args:
        customer_id: UUID of the customer
        limit: Maximum number of messages to retrieve (default 10)
    """
    return await mcp_get_customer_history(customer_id=customer_id, limit=limit)


@mcp.tool()
async def escalate_to_human(
    customer_id: str,
    ticket_id: str,
    reason: str,
    conversation_id: str = "",
    notes: str = "",
) -> str:
    """Escalate the conversation to a human support agent.

    Args:
        customer_id: UUID of the customer
        ticket_id: UUID of the ticket
        reason: Escalation reason code
        conversation_id: UUID of the active conversation
        notes: Additional context for the human agent
    """
    return await mcp_escalate_to_human(
        customer_id=customer_id, ticket_id=ticket_id, reason=reason,
        conversation_id=conversation_id, notes=notes,
    )


@mcp.tool()
async def send_response(
    customer_id: str,
    conversation_id: str,
    channel: str,
    response_text: str,
    ticket_number: str = "",
    customer_name: str = "",
) -> str:
    """Format and send a response to the customer via their channel.

    Args:
        customer_id: UUID of the customer
        conversation_id: UUID of the active conversation
        channel: One of: email, whatsapp, web_form
        response_text: The agent's response content
        ticket_number: Ticket number to include in response
        customer_name: Customer's first name for personalization
    """
    return await mcp_send_response(
        customer_id=customer_id, conversation_id=conversation_id,
        channel=channel, response_text=response_text,
        ticket_number=ticket_number, customer_name=customer_name,
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
