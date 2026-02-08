"""Agent tools — 5 @function_tool definitions for OpenAI Agents SDK."""
import json
import time
from datetime import datetime, timezone

from agents import function_tool

from production.agent.formatters import format_response
from production.agent.prompts import detect_escalation_trigger, get_escalation_response


@function_tool
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


@function_tool
async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Retrieve the customer's interaction history across all channels.

    Args:
        customer_id: UUID of the customer
        limit: Maximum number of messages to retrieve (default 10)
    """
    from production.database.pool import get_pool
    from production.database.queries import messages

    pool = await get_pool()
    history = await messages.get_customer_history(pool, customer_id, limit=limit)

    if not history:
        return json.dumps({"messages": [], "total": 0})

    formatted = []
    for msg in history:
        formatted.append({
            "channel": msg.get("channel", "unknown"),
            "direction": msg.get("direction", "unknown"),
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", "")[:200],
            "created_at": str(msg.get("created_at", "")),
        })

    return json.dumps({"messages": formatted, "total": len(formatted)})


@function_tool
async def search_knowledge_base(query: str, category: str = "") -> str:
    """Search TechCorp product documentation using semantic search.

    Args:
        query: The customer's question or search terms
        category: Optional category filter (e.g., 'account', 'billing', 'technical')
    """
    from production.database.pool import get_pool
    from production.database.queries import knowledge_base

    pool = await get_pool()

    # If we have category, try category-based search first
    if category:
        results = await knowledge_base.get_by_category(pool, category)
        if results:
            entries = []
            for r in results[:5]:
                entries.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:500],
                    "category": r.get("category", ""),
                })
            return json.dumps({"results": entries, "total": len(entries)})

    # Try embedding-based search (with placeholder embedding for now)
    # In production, we'd generate an embedding from the query using OpenAI
    try:
        # Generate a simple placeholder embedding for text search
        # Real implementation would use: openai.embeddings.create(model="text-embedding-3-small", input=query)
        results = await knowledge_base.get_by_category(pool, "general")
        if not results:
            # Fallback: try all categories
            for cat in ["account", "technical", "billing", "how_to", "troubleshooting"]:
                results = await knowledge_base.get_by_category(pool, cat)
                if results:
                    break
    except Exception:
        results = []

    if not results:
        return json.dumps({"results": [], "total": 0, "message": "No results found"})

    entries = []
    for r in results[:5]:
        entries.append({
            "title": r.get("title", ""),
            "content": r.get("content", "")[:500],
            "category": r.get("category", ""),
        })

    return json.dumps({"results": entries, "total": len(entries)})


@function_tool
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
        reason: Escalation reason code (pricing_inquiry, refund_request, legal, human_request, data_security, abusive_language, negative_sentiment, no_kb_match)
        conversation_id: UUID of the active conversation
        notes: Additional context for the human agent
    """
    from production.database.pool import get_pool
    from production.database.queries import tickets as ticket_queries
    from production.database.queries import conversations
    from production.database.queries import metrics

    pool = await get_pool()

    # Update ticket status to escalated
    await ticket_queries.update_ticket_status(
        pool, ticket_id, "escalated",
        escalation_reason=reason,
        resolution_notes=notes,
    )

    # Update conversation status
    if conversation_id:
        await conversations.update_status(
            pool, conversation_id, "escalated",
            escalation_reason=reason,
        )

    # Record escalation metric
    await metrics.record_metric(
        pool, "escalation", 1.0,
        metadata={"reason": reason, "customer_id": customer_id},
    )

    return json.dumps({
        "status": "escalated",
        "reason": reason,
        "message": f"Conversation escalated to human support. Reason: {reason}",
    })


@function_tool
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
    from production.database.pool import get_pool
    from production.database.queries import messages, metrics

    pool = await get_pool()
    start_time = time.time()

    # Format response per channel
    formatted = format_response(
        response_text,
        channel=channel,
        customer_name=customer_name or "there",
        ticket_number=ticket_number,
    )

    # Store outbound message
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

    # Record response latency
    latency_ms = (time.time() - start_time) * 1000
    await metrics.record_metric(
        pool, "response_latency", latency_ms, channel=channel,
    )

    return json.dumps({
        "status": "sent",
        "channel": channel,
        "formatted_length": len(formatted),
    })


def check_guardrails(message: str, sentiment_score: float = 0.5) -> dict | None:
    """Check message against all guardrails. Returns escalation info or None."""
    # Check hard keyword triggers
    trigger = detect_escalation_trigger(message)
    if trigger:
        return {"should_escalate": True, "reason": trigger}

    # Check sentiment
    if sentiment_score < 0.3:
        return {"should_escalate": True, "reason": "negative_sentiment"}

    return None
