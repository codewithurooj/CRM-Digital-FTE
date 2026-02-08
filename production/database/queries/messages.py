"""Message storage and retrieval queries."""
import json


async def store_message(pool, conversation_id, customer_id, channel, direction, role,
                        content, content_type="text", metadata=None):
    """Store a message (inbound or outbound)."""
    meta_json = json.dumps(metadata or {})
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO messages
               (conversation_id, customer_id, channel, direction, role, content, content_type, metadata)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
               RETURNING *""",
            conversation_id, customer_id, channel, direction, role,
            content, content_type, meta_json,
        )
        return dict(row) if row else None


async def get_messages_by_conversation(pool, conversation_id, limit=50):
    """Get messages for a conversation, ordered chronologically."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM messages
               WHERE conversation_id = $1
               ORDER BY created_at ASC
               LIMIT $2""",
            conversation_id, limit,
        )
        return [dict(r) for r in rows]


async def get_customer_history(pool, customer_id, limit=20):
    """Get all messages for a customer across all channels."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT m.*, c.channel AS conv_channel
               FROM messages m
               JOIN conversations c ON m.conversation_id = c.id
               WHERE m.customer_id = $1
               ORDER BY m.created_at DESC
               LIMIT $2""",
            customer_id, limit,
        )
        return [dict(r) for r in rows]


async def get_full_customer_history(pool, customer_id):
    """Get complete message history for a customer across ALL channels."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT m.*, c.channel AS conv_channel
               FROM messages m
               JOIN conversations c ON m.conversation_id = c.id
               WHERE m.customer_id = $1
               ORDER BY m.created_at ASC""",
            customer_id,
        )
        return [dict(r) for r in rows]
