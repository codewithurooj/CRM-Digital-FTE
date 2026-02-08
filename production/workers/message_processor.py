"""Kafka message processor worker — consume from fte.tickets.incoming, run agent, route response."""
import json
import logging
import re
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# --- Sentiment Scoring (Phase 14: T105) ---

NEGATIVE_WORDS = {
    "terrible", "awful", "horrible", "worst", "broken", "unusable", "ridiculous",
    "unacceptable", "frustrated", "furious", "angry", "disappointed", "pathetic",
    "useless", "rubbish", "disgusting", "outrageous", "absurd", "failing", "hate",
    "slow", "buggy", "crashing", "missing", "lost", "down", "error",
}
POSITIVE_WORDS = {
    "great", "thanks", "thank", "please", "appreciate", "wonderful", "excellent",
    "helpful", "love", "fantastic", "perfect", "good", "nice", "happy", "amazing",
    "awesome", "easy", "works", "solved", "fixed", "resolved",
}


def score_sentiment(text: str) -> float:
    """Score message sentiment from 0.0 (very negative) to 1.0 (very positive).

    Uses a keyword-based approach for speed and determinism.
    """
    words = set(re.findall(r'\b\w+\b', text.lower()))
    neg_count = len(words & NEGATIVE_WORDS)
    pos_count = len(words & POSITIVE_WORDS)

    # Check for ALL CAPS (anger signal)
    alpha_chars = re.sub(r'[^a-zA-Z]', '', text)
    if len(alpha_chars) > 10 and alpha_chars == alpha_chars.upper():
        neg_count += 3

    # Check for excessive punctuation (!!!, ???)
    if text.count('!') >= 3 or text.count('?') >= 3:
        neg_count += 1

    total = neg_count + pos_count
    if total == 0:
        return 0.5  # neutral

    score = pos_count / total
    # Clamp and smooth toward center
    return max(0.05, min(0.95, score * 0.8 + 0.1))


def route_priority_by_sentiment(sentiment: float, current_priority: str) -> str:
    """Adjust ticket priority based on sentiment score (T106).

    - sentiment < 0.3 → force "high" (auto-escalate candidate)
    - sentiment 0.3-0.5 → bump to at least "high"
    - sentiment > 0.5 → keep current priority
    """
    if sentiment < 0.3:
        return "high"
    if sentiment < 0.5 and current_priority == "low":
        return "high"
    return current_priority


async def process_kafka_message(raw_message: bytes) -> dict:
    """Process a single Kafka message from fte.tickets.incoming.

    Pipeline:
    1. Deserialize message
    2. Resolve customer identity
    3. Create/resume conversation
    4. Run AI agent
    5. Store response in DB
    6. Route to outbound channel

    Returns dict with processing result.
    """
    from production.database.pool import get_pool
    from production.database.queries import customers, conversations, messages, metrics
    from production.channels import get_handler

    pool = await get_pool()
    start_time = time.time()

    try:
        # 1. Deserialize
        msg_data = json.loads(raw_message)
        customer_identifier = msg_data["customer_identifier"]
        identifier_type = msg_data["identifier_type"]
        channel = msg_data["channel"]
        content = msg_data["content"]
        subject = msg_data.get("subject")
        metadata = msg_data.get("metadata", {})

        logger.info(f"Processing message: channel={channel}, identifier={customer_identifier[:20]}...")

        # 2. Resolve customer identity
        customer = await customers.resolve_customer_identity(
            pool, customer_identifier, identifier_type, channel,
        )

        if not customer:
            raise RuntimeError(f"Failed to resolve customer: {customer_identifier}")

        customer_id = customer["id"]
        customer_name = customer.get("name", "")

        # 3. Create or resume conversation
        active_convos = await conversations.get_active_by_customer(pool, customer_id)
        if active_convos:
            conversation = active_convos[0]
        else:
            conversation = await conversations.create_conversation(pool, customer_id, channel)

        conversation_id = conversation["id"]

        # 4. Score sentiment (T105)
        sentiment = score_sentiment(content)

        # 4a. Store inbound message with sentiment
        await messages.store_message(
            pool,
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            direction="inbound",
            role="customer",
            content=content,
            metadata={"subject": subject, "sentiment_score": sentiment, **(metadata or {})},
        )

        # 4b. Record sentiment metric
        await metrics.record_metric(
            pool, "sentiment", sentiment, channel=channel,
            metadata={"customer_id": str(customer_id)},
        )

        # 4c. Adjust priority based on sentiment (T106)
        current_priority = metadata.get("priority", "medium")
        adjusted_priority = route_priority_by_sentiment(sentiment, current_priority)
        if adjusted_priority != current_priority:
            logger.info(f"Sentiment routing: priority {current_priority} → {adjusted_priority} (sentiment={sentiment:.2f})")

        # 5. Run AI agent with sentiment score
        from production.agent.customer_success_agent import process_message
        agent_result = await process_message(
            customer_id=str(customer_id),
            conversation_id=str(conversation_id),
            channel=channel,
            message=content,
            customer_name=customer_name,
            sentiment_score=sentiment,
        )

        # 6. Record processing latency
        latency_ms = (time.time() - start_time) * 1000
        await metrics.record_metric(
            pool, "response_latency", latency_ms, channel=channel,
        )
        await metrics.record_metric(
            pool, "conversation_count", 1.0, channel=channel,
        )
        await metrics.record_metric(
            pool, "message_volume", 1.0, channel=channel,
        )

        logger.info(
            f"Message processed: channel={channel}, "
            f"escalated={agent_result.get('escalated', False)}, "
            f"latency={latency_ms:.0f}ms"
        )

        return {
            "status": "processed",
            "customer_id": str(customer_id),
            "conversation_id": str(conversation_id),
            "channel": channel,
            "escalated": agent_result.get("escalated", False),
            "latency_ms": latency_ms,
            "sentiment": sentiment,
            "priority": adjusted_priority,
        }

    except Exception as e:
        logger.error(f"Message processing failed: {e}", exc_info=True)
        # Attempt to send apologetic response
        await _send_error_response(raw_message, str(e))
        return {"status": "failed", "error": str(e)}


async def _send_error_response(raw_message: bytes, error: str):
    """Send an apologetic response when processing fails."""
    try:
        msg_data = json.loads(raw_message)
        channel = msg_data.get("channel", "web_form")
        customer_identifier = msg_data.get("customer_identifier", "")

        from production.channels import get_handler
        handler = get_handler(channel)

        fallback_text = (
            "We're experiencing high demand right now and weren't able to fully process "
            "your request. A member of our team will follow up with you shortly. "
            "We apologize for the inconvenience."
        )
        formatted = await handler.format_response(fallback_text, {})
        await handler.deliver(formatted, customer_identifier, {})
    except Exception as e2:
        logger.error(f"Failed to send error response: {e2}")


async def run_worker():
    """Main worker loop — consume messages from Kafka and process them."""
    from aiokafka import AIOKafkaConsumer
    from production.config import get_settings
    from production.kafka_client import get_producer

    settings = get_settings()

    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_INCOMING,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="fte-worker-group",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    await consumer.start()
    producer = await get_producer()
    logger.info(f"Worker started, consuming from {settings.KAFKA_TOPIC_INCOMING}")

    try:
        async for msg in consumer:
            try:
                result = await process_kafka_message(msg.value)

                if result["status"] == "failed":
                    # Publish to DLQ
                    await producer.send_and_wait(
                        settings.KAFKA_TOPIC_DLQ,
                        json.dumps({
                            "original_message": msg.value.decode("utf-8"),
                            "error": result.get("error", "unknown"),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }).encode("utf-8"),
                    )

                # Commit offset after successful processing
                await consumer.commit()

            except Exception as e:
                logger.error(f"Worker iteration failed: {e}", exc_info=True)
                # Publish to DLQ
                try:
                    await producer.send_and_wait(
                        settings.KAFKA_TOPIC_DLQ,
                        json.dumps({
                            "original_message": msg.value.decode("utf-8"),
                            "error": str(e),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }).encode("utf-8"),
                    )
                    await consumer.commit()
                except Exception:
                    pass

    finally:
        await consumer.stop()
        logger.info("Worker stopped")
