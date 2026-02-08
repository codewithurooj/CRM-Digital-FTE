"""Kafka producer/consumer factory — lazy singleton pattern."""
import logging

logger = logging.getLogger(__name__)

_producer = None
_consumer = None


async def get_producer():
    """Return or create the Kafka producer (lazy singleton)."""
    global _producer
    if _producer is None:
        from production.config import get_settings
        settings = get_settings()
        from aiokafka import AIOKafkaProducer
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        )
        await _producer.start()
        logger.info(f"Kafka producer started: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    return _producer


async def get_consumer(topic: str = None, group_id: str = "fte-worker-group"):
    """Return or create a Kafka consumer."""
    global _consumer
    if _consumer is None:
        from production.config import get_settings
        settings = get_settings()
        from aiokafka import AIOKafkaConsumer
        _consumer = AIOKafkaConsumer(
            topic or settings.KAFKA_TOPIC_INCOMING,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await _consumer.start()
        logger.info(f"Kafka consumer started: topic={topic or settings.KAFKA_TOPIC_INCOMING}")
    return _consumer


async def close_producer():
    """Close the Kafka producer if it exists."""
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def close_consumer():
    """Close the Kafka consumer if it exists."""
    global _consumer
    if _consumer is not None:
        await _consumer.stop()
        _consumer = None
        logger.info("Kafka consumer stopped")


def reset_producer():
    """Reset producer reference (for testing)."""
    global _producer
    _producer = None


def reset_consumer():
    """Reset consumer reference (for testing)."""
    global _consumer
    _consumer = None
