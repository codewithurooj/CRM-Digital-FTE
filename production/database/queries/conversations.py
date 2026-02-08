"""Conversation lifecycle queries."""


async def create_conversation(pool, customer_id, channel):
    """Create a new conversation thread."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO conversations (customer_id, channel)
               VALUES ($1, $2) RETURNING *""",
            customer_id, channel,
        )
        return dict(row) if row else None


async def get_conversation(pool, conversation_id):
    """Get a conversation by ID."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM conversations WHERE id = $1", conversation_id
        )
        return dict(row) if row else None


async def update_status(pool, conversation_id, status, resolution_type=None, escalation_reason=None):
    """Update conversation status."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE conversations
               SET status = $2, resolution_type = $3, escalation_reason = $4
               WHERE id = $1 RETURNING *""",
            conversation_id, status, resolution_type, escalation_reason,
        )
        return dict(row) if row else None


async def close_conversation(pool, conversation_id, resolution_type="resolved"):
    """Close a conversation."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE conversations
               SET status = 'closed', resolution_type = $2, closed_at = NOW()
               WHERE id = $1 RETURNING *""",
            conversation_id, resolution_type,
        )
        return dict(row) if row else None


async def get_active_by_customer(pool, customer_id):
    """Get active conversations for a customer."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM conversations
               WHERE customer_id = $1 AND status = 'active'
               ORDER BY created_at DESC""",
            customer_id,
        )
        return [dict(r) for r in rows]
