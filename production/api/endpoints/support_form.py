"""Web support form endpoint — POST /api/v1/support/form."""
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from production.api.dependencies import get_db_pool, get_kafka_producer
from production.schemas.support_form import SupportFormRequest, SupportFormResponse
from production.database.queries import customers, conversations, messages, tickets

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/support/form", status_code=201, response_model=SupportFormResponse)
async def submit_support_form(
    form: SupportFormRequest,
    pool=Depends(get_db_pool),
):
    """Accept a web support form submission. Creates ticket and returns ticket ID within 500ms."""
    try:
        # 1. Resolve or create customer
        customer = await customers.get_customer_by_email(pool, form.email)
        if not customer:
            customer = await customers.create_customer(
                pool, email=form.email, name=form.name,
            )
            if customer:
                await customers.create_identifier(
                    pool, customer["id"], "email", form.email, "web_form",
                )

        if not customer:
            raise HTTPException(status_code=503, detail="SERVICE_UNAVAILABLE")

        # 2. Create conversation
        conversation = await conversations.create_conversation(
            pool, customer["id"], "web_form",
        )

        # 3. Store inbound message
        await messages.store_message(
            pool,
            conversation_id=conversation["id"],
            customer_id=customer["id"],
            channel="web_form",
            direction="inbound",
            role="customer",
            content=form.message,
            metadata={"subject": form.subject, "category": form.category.value},
        )

        # 4. Create ticket
        ticket = await tickets.create_ticket(
            pool,
            customer_id=customer["id"],
            subject=form.subject,
            category=form.category.value,
            source_channel="web_form",
            priority=form.priority.value,
            conversation_id=conversation["id"],
        )

        if not ticket:
            raise HTTPException(status_code=503, detail="SERVICE_UNAVAILABLE")

        # 5. Publish to Kafka for async agent processing
        try:
            from production.kafka_client import get_producer
            from production.config import get_settings
            settings = get_settings()
            producer = await get_producer()
            await producer.send_and_wait(
                settings.KAFKA_TOPIC_INCOMING,
                json.dumps({
                    "customer_identifier": form.email,
                    "identifier_type": "email",
                    "channel": "web_form",
                    "content": form.message,
                    "subject": form.subject,
                    "metadata": {
                        "name": form.name,
                        "category": form.category.value,
                        "priority": form.priority.value,
                        "ticket_number": ticket["ticket_number"],
                        "customer_id": str(customer["id"]),
                        "conversation_id": str(conversation["id"]),
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }).encode("utf-8"),
            )
        except Exception as e:
            # Kafka publish failure is non-blocking — ticket already created
            logger.warning(f"Kafka publish failed (non-blocking): {e}")

        return SupportFormResponse(
            ticket_id=ticket["ticket_number"],
            status="received",
            created_at=ticket.get("created_at", datetime.now(timezone.utc)),
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="SERVICE_UNAVAILABLE")
