"""Unit tests for Kafka client — producer/consumer creation, close, reset, singleton."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import production.kafka_client as kafka_mod
from production.kafka_client import (
    get_producer, get_consumer, close_producer, close_consumer,
    reset_producer, reset_consumer,
)


class TestKafkaProducer:
    def setup_method(self):
        reset_producer()

    def test_reset_clears_producer(self):
        reset_producer()
        assert kafka_mod._producer is None

    @pytest.mark.asyncio
    async def test_get_producer_creates_and_starts(self):
        """get_producer creates AIOKafkaProducer and calls start()."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaProducer", return_value=mock_instance):
            result = await get_producer()

        assert result is mock_instance
        mock_instance.start.assert_called_once()
        reset_producer()

    @pytest.mark.asyncio
    async def test_get_producer_returns_singleton(self):
        """Second call returns same instance without creating new."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaProducer", return_value=mock_instance) as mock_cls:
            first = await get_producer()
            second = await get_producer()

        assert first is second
        mock_cls.assert_called_once()  # Only one constructor call
        reset_producer()

    @pytest.mark.asyncio
    async def test_close_producer_stops_and_resets(self):
        """close_producer calls stop() and sets reference to None."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()
        mock_instance.stop = AsyncMock()

        with patch("aiokafka.AIOKafkaProducer", return_value=mock_instance):
            await get_producer()

        await close_producer()
        mock_instance.stop.assert_called_once()
        assert kafka_mod._producer is None

    @pytest.mark.asyncio
    async def test_close_producer_when_none(self):
        """close_producer with no active producer is a no-op."""
        reset_producer()
        await close_producer()  # Should not raise

    def test_topic_names_from_config(self):
        from production.config import get_settings
        settings = get_settings()
        assert settings.KAFKA_TOPIC_INCOMING == "fte.tickets.incoming"
        assert settings.KAFKA_TOPIC_OUTGOING == "fte.tickets.outgoing"
        assert settings.KAFKA_TOPIC_DLQ == "fte.tickets.dlq"


class TestKafkaConsumer:
    def setup_method(self):
        reset_consumer()

    @pytest.mark.asyncio
    async def test_get_consumer_creates_and_starts(self):
        """get_consumer creates AIOKafkaConsumer and calls start()."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaConsumer", return_value=mock_instance):
            result = await get_consumer(topic="test.topic")

        assert result is mock_instance
        mock_instance.start.assert_called_once()
        reset_consumer()

    @pytest.mark.asyncio
    async def test_get_consumer_uses_default_topic(self):
        """get_consumer without topic arg uses config default."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaConsumer", return_value=mock_instance) as mock_cls:
            await get_consumer()

        call_args = mock_cls.call_args
        assert call_args[0][0] == "fte.tickets.incoming"
        reset_consumer()

    @pytest.mark.asyncio
    async def test_get_consumer_returns_singleton(self):
        """Second call returns same instance."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaConsumer", return_value=mock_instance) as mock_cls:
            first = await get_consumer()
            second = await get_consumer()

        assert first is second
        mock_cls.assert_called_once()
        reset_consumer()

    @pytest.mark.asyncio
    async def test_close_consumer_stops_and_resets(self):
        """close_consumer calls stop() and sets reference to None."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()
        mock_instance.stop = AsyncMock()

        with patch("aiokafka.AIOKafkaConsumer", return_value=mock_instance):
            await get_consumer()

        await close_consumer()
        mock_instance.stop.assert_called_once()
        assert kafka_mod._consumer is None

    @pytest.mark.asyncio
    async def test_close_consumer_when_none(self):
        """close_consumer with no active consumer is a no-op."""
        reset_consumer()
        await close_consumer()  # Should not raise

    def test_reset_consumer_clears(self):
        reset_consumer()
        assert kafka_mod._consumer is None

    @pytest.mark.asyncio
    async def test_get_consumer_custom_group_id(self):
        """get_consumer passes custom group_id to constructor."""
        mock_instance = AsyncMock()
        mock_instance.start = AsyncMock()

        with patch("aiokafka.AIOKafkaConsumer", return_value=mock_instance) as mock_cls:
            await get_consumer(group_id="custom-group")

        call_kwargs = mock_cls.call_args
        assert call_kwargs[1]["group_id"] == "custom-group"
        reset_consumer()
