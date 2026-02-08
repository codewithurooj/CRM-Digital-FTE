"""Unit tests for message_processor — process_kafka_message, _send_error_response, run_worker."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from production.tests.conftest import make_mock_pool


def _make_kafka_message(data: dict) -> bytes:
    """Helper to create a raw Kafka message."""
    return json.dumps(data).encode("utf-8")


def _valid_message_data():
    return {
        "customer_identifier": "alice@example.com",
        "identifier_type": "email",
        "channel": "web_form",
        "content": "How do I reset my password?",
        "subject": "Password help",
        "metadata": {"priority": "medium"},
    }


class TestProcessKafkaMessage:
    """Tests for process_kafka_message() — the main pipeline function."""

    @pytest.mark.asyncio
    async def test_successful_processing(self):
        """Happy path: message → identity → conversation → agent → metrics."""
        pool, conn = make_mock_pool()
        msg = _make_kafka_message(_valid_message_data())

        mock_customer = {"id": "cust-1", "name": "Alice"}
        mock_conversation = {"id": "conv-1"}
        mock_agent_result = {"escalated": False, "status": "success", "response": "Here's how..."}

        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool), \
             patch("production.database.queries.customers.resolve_customer_identity", new_callable=AsyncMock, return_value=mock_customer), \
             patch("production.database.queries.conversations.get_active_by_customer", new_callable=AsyncMock, return_value=[]), \
             patch("production.database.queries.conversations.create_conversation", new_callable=AsyncMock, return_value=mock_conversation), \
             patch("production.database.queries.messages.store_message", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock), \
             patch("production.agent.customer_success_agent.process_message", new_callable=AsyncMock, return_value=mock_agent_result):

            from production.workers.message_processor import process_kafka_message
            result = await process_kafka_message(msg)

        assert result["status"] == "processed"
        assert result["customer_id"] == "cust-1"
        assert result["conversation_id"] == "conv-1"
        assert result["channel"] == "web_form"
        assert "sentiment" in result
        assert "priority" in result
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_resumes_existing_conversation(self):
        """When active conversation exists, reuses it instead of creating new."""
        pool, conn = make_mock_pool()
        msg = _make_kafka_message(_valid_message_data())

        existing_convo = {"id": "conv-existing"}

        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool), \
             patch("production.database.queries.customers.resolve_customer_identity", new_callable=AsyncMock, return_value={"id": "c1", "name": "A"}), \
             patch("production.database.queries.conversations.get_active_by_customer", new_callable=AsyncMock, return_value=[existing_convo]), \
             patch("production.database.queries.conversations.create_conversation", new_callable=AsyncMock) as mock_create, \
             patch("production.database.queries.messages.store_message", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock), \
             patch("production.agent.customer_success_agent.process_message", new_callable=AsyncMock, return_value={"escalated": False}):

            from production.workers.message_processor import process_kafka_message
            result = await process_kafka_message(msg)

        assert result["conversation_id"] == "conv-existing"
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_customer_resolution_failure(self):
        """When customer identity cannot be resolved, returns failed."""
        pool, conn = make_mock_pool()
        msg = _make_kafka_message(_valid_message_data())

        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool), \
             patch("production.database.queries.customers.resolve_customer_identity", new_callable=AsyncMock, return_value=None), \
             patch("production.channels.get_handler") as mock_handler_fn:

            mock_handler = AsyncMock()
            mock_handler.format_response = AsyncMock(return_value="sorry")
            mock_handler.deliver = AsyncMock(return_value=True)
            mock_handler_fn.return_value = mock_handler

            from production.workers.message_processor import process_kafka_message
            result = await process_kafka_message(msg)

        assert result["status"] == "failed"
        assert "Failed to resolve customer" in result["error"]

    @pytest.mark.asyncio
    async def test_invalid_json_fails(self):
        """Non-JSON message returns failed status."""
        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=MagicMock()), \
             patch("production.channels.get_handler") as mock_handler_fn:

            mock_handler = AsyncMock()
            mock_handler.format_response = AsyncMock(return_value="sorry")
            mock_handler.deliver = AsyncMock(return_value=True)
            mock_handler_fn.return_value = mock_handler

            from production.workers.message_processor import process_kafka_message
            result = await process_kafka_message(b"not json at all")

        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_sentiment_recorded_in_metrics(self):
        """Sentiment score is recorded as a metric."""
        pool, conn = make_mock_pool()
        msg = _make_kafka_message(_valid_message_data())

        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool), \
             patch("production.database.queries.customers.resolve_customer_identity", new_callable=AsyncMock, return_value={"id": "c1", "name": "A"}), \
             patch("production.database.queries.conversations.get_active_by_customer", new_callable=AsyncMock, return_value=[]), \
             patch("production.database.queries.conversations.create_conversation", new_callable=AsyncMock, return_value={"id": "conv-1"}), \
             patch("production.database.queries.messages.store_message", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock) as mock_metric, \
             patch("production.agent.customer_success_agent.process_message", new_callable=AsyncMock, return_value={"escalated": False}):

            from production.workers.message_processor import process_kafka_message
            await process_kafka_message(msg)

        # Check that sentiment was recorded
        sentiment_calls = [c for c in mock_metric.call_args_list if c[0][1] == "sentiment"]
        assert len(sentiment_calls) >= 1

    @pytest.mark.asyncio
    async def test_negative_sentiment_adjusts_priority(self):
        """Very negative message bumps priority."""
        pool, conn = make_mock_pool()
        data = _valid_message_data()
        data["content"] = "This is terrible and broken! The worst product ever!!!"
        data["metadata"] = {"priority": "low"}
        msg = _make_kafka_message(data)

        with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool), \
             patch("production.database.queries.customers.resolve_customer_identity", new_callable=AsyncMock, return_value={"id": "c1", "name": "A"}), \
             patch("production.database.queries.conversations.get_active_by_customer", new_callable=AsyncMock, return_value=[]), \
             patch("production.database.queries.conversations.create_conversation", new_callable=AsyncMock, return_value={"id": "conv-1"}), \
             patch("production.database.queries.messages.store_message", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock), \
             patch("production.agent.customer_success_agent.process_message", new_callable=AsyncMock, return_value={"escalated": True}):

            from production.workers.message_processor import process_kafka_message
            result = await process_kafka_message(msg)

        assert result["priority"] == "high"


class TestSendErrorResponse:
    """Tests for _send_error_response() — fallback when processing fails."""

    @pytest.mark.asyncio
    async def test_sends_fallback_message(self):
        """Error response sends apologetic message via the right channel."""
        msg = _make_kafka_message(_valid_message_data())

        mock_handler = AsyncMock()
        mock_handler.format_response = AsyncMock(return_value="We're sorry...")
        mock_handler.deliver = AsyncMock(return_value=True)

        with patch("production.channels.get_handler", return_value=mock_handler):
            from production.workers.message_processor import _send_error_response
            await _send_error_response(msg, "test error")

        mock_handler.format_response.assert_called_once()
        mock_handler.deliver.assert_called_once()
        # Verify correct destination
        deliver_args = mock_handler.deliver.call_args
        assert deliver_args[0][1] == "alice@example.com"

    @pytest.mark.asyncio
    async def test_error_response_handles_invalid_json(self):
        """If raw_message is invalid JSON, _send_error_response doesn't crash."""
        from production.workers.message_processor import _send_error_response
        # Should not raise
        await _send_error_response(b"not json", "some error")

    @pytest.mark.asyncio
    async def test_error_response_handles_delivery_failure(self):
        """If delivery fails, _send_error_response doesn't crash."""
        msg = _make_kafka_message(_valid_message_data())

        mock_handler = AsyncMock()
        mock_handler.format_response = AsyncMock(side_effect=Exception("delivery failed"))

        with patch("production.channels.get_handler", return_value=mock_handler):
            from production.workers.message_processor import _send_error_response
            # Should not raise
            await _send_error_response(msg, "test error")


class TestRunWorker:
    """Tests for run_worker() — Kafka consumer loop."""

    @pytest.mark.asyncio
    async def test_processes_message_and_commits(self):
        """Worker consumes message, processes it, and commits offset."""
        mock_msg = MagicMock()
        mock_msg.value = _make_kafka_message(_valid_message_data())

        mock_consumer = AsyncMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()
        mock_consumer.commit = AsyncMock()

        # Make consumer yield one message then stop
        async def mock_iter():
            yield mock_msg

        mock_consumer.__aiter__ = lambda self: mock_iter()

        mock_producer = AsyncMock()
        mock_producer.send_and_wait = AsyncMock()

        processed_result = {"status": "processed", "escalated": False}

        with patch("production.workers.message_processor.process_kafka_message", new_callable=AsyncMock, return_value=processed_result) as mock_process, \
             patch("production.kafka_client.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("aiokafka.AIOKafkaConsumer", return_value=mock_consumer):

            from production.workers.message_processor import run_worker
            await run_worker()

        mock_process.assert_called_once_with(mock_msg.value)
        mock_consumer.commit.assert_called_once()
        mock_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_failed_message_publishes_to_dlq(self):
        """Failed processing publishes to DLQ topic."""
        mock_msg = MagicMock()
        mock_msg.value = _make_kafka_message(_valid_message_data())

        mock_consumer = AsyncMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()
        mock_consumer.commit = AsyncMock()

        async def mock_iter():
            yield mock_msg

        mock_consumer.__aiter__ = lambda self: mock_iter()

        mock_producer = AsyncMock()
        mock_producer.send_and_wait = AsyncMock()

        failed_result = {"status": "failed", "error": "test failure"}

        with patch("production.workers.message_processor.process_kafka_message", new_callable=AsyncMock, return_value=failed_result), \
             patch("production.kafka_client.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("aiokafka.AIOKafkaConsumer", return_value=mock_consumer):

            from production.workers.message_processor import run_worker
            await run_worker()

        # DLQ publish should happen
        mock_producer.send_and_wait.assert_called_once()
        dlq_call = mock_producer.send_and_wait.call_args
        assert dlq_call[0][0] == "fte.tickets.dlq"
        dlq_payload = json.loads(dlq_call[0][1].decode("utf-8"))
        assert dlq_payload["error"] == "test failure"

    @pytest.mark.asyncio
    async def test_exception_during_processing_publishes_dlq(self):
        """Unhandled exception in loop still publishes to DLQ."""
        mock_msg = MagicMock()
        mock_msg.value = _make_kafka_message(_valid_message_data())

        mock_consumer = AsyncMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()
        mock_consumer.commit = AsyncMock()

        async def mock_iter():
            yield mock_msg

        mock_consumer.__aiter__ = lambda self: mock_iter()

        mock_producer = AsyncMock()
        mock_producer.send_and_wait = AsyncMock()

        with patch("production.workers.message_processor.process_kafka_message", new_callable=AsyncMock, side_effect=RuntimeError("boom")), \
             patch("production.kafka_client.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("aiokafka.AIOKafkaConsumer", return_value=mock_consumer):

            from production.workers.message_processor import run_worker
            await run_worker()

        # DLQ publish should happen for exception path
        mock_producer.send_and_wait.assert_called_once()
        mock_consumer.stop.assert_called_once()
