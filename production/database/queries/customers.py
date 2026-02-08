"""Customer CRUD queries + identity resolution."""
import json


async def create_customer(pool, email, name=None, phone=None, company=None, plan="free"):
    """Create a new customer record."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO customers (email, name, phone, company, plan)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING *""",
            email, name, phone, company, plan,
        )
        return dict(row) if row else None


async def get_customer_by_email(pool, email):
    """Find a customer by email."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM customers WHERE email = $1", email)
        return dict(row) if row else None


async def get_customer_by_id(pool, customer_id):
    """Find a customer by UUID."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM customers WHERE id = $1", customer_id)
        return dict(row) if row else None


async def update_customer(pool, customer_id, **fields):
    """Update customer fields dynamically."""
    if not fields:
        return None
    set_clauses = []
    values = []
    for i, (key, val) in enumerate(fields.items(), start=1):
        set_clauses.append(f"{key} = ${i}")
        values.append(val)
    values.append(customer_id)
    query = f"""UPDATE customers SET {', '.join(set_clauses)}
                WHERE id = ${len(values)} RETURNING *"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)
        return dict(row) if row else None


async def resolve_identity(pool, identifier_value, identifier_type):
    """Resolve a customer by identifier (cross-channel lookup)."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT c.* FROM customers c
               JOIN customer_identifiers ci ON c.id = ci.customer_id
               WHERE ci.identifier_type = $1 AND ci.identifier_value = $2""",
            identifier_type, identifier_value,
        )
        return dict(row) if row else None


async def create_identifier(pool, customer_id, identifier_type, identifier_value, channel):
    """Create a customer identifier for cross-channel matching."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, channel)
               VALUES ($1, $2, $3, $4)
               ON CONFLICT (identifier_type, identifier_value) DO NOTHING
               RETURNING *""",
            customer_id, identifier_type, identifier_value, channel,
        )
        return dict(row) if row else None


async def resolve_customer_identity(pool, identifier_value, identifier_type, channel):
    """Resolve or create customer from an identifier."""
    # Try identifier table first
    customer = await resolve_identity(pool, identifier_value, identifier_type)
    if customer:
        return customer

    # Try direct email match
    if identifier_type == "email":
        customer = await get_customer_by_email(pool, identifier_value)
        if customer:
            await create_identifier(pool, customer["id"], identifier_type, identifier_value, channel)
            return customer

    # Create new customer
    email = identifier_value if identifier_type == "email" else f"{identifier_value}@unknown.local"
    phone = identifier_value if identifier_type == "phone" else None
    customer = await create_customer(pool, email=email, phone=phone)
    if customer:
        await create_identifier(pool, customer["id"], identifier_type, identifier_value, channel)
    return customer
