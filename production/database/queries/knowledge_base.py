"""Knowledge base queries with pgvector semantic search."""


async def search_by_embedding(pool, embedding_vector, limit=5):
    """Search knowledge base by vector similarity (pgvector cosine)."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, title, content, category,
                      1 - (embedding <=> $1::vector) AS similarity
               FROM knowledge_base
               WHERE is_active = TRUE
               ORDER BY embedding <=> $1::vector
               LIMIT $2""",
            str(embedding_vector), limit,
        )
        return [dict(r) for r in rows]


async def insert_entry(pool, title, content, category, source="product-docs", embedding=None):
    """Insert a knowledge base entry."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO knowledge_base (title, content, category, source, embedding)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING *""",
            title, content, category, source, str(embedding) if embedding else None,
        )
        return dict(row) if row else None


async def get_by_category(pool, category):
    """Get knowledge base entries by category."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM knowledge_base
               WHERE category = $1 AND is_active = TRUE
               ORDER BY title""",
            category,
        )
        return [dict(r) for r in rows]
