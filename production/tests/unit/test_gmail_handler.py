"""Unit tests for Gmail channel handler — parse and format."""
import base64
import json
import pytest

from production.channels.gmail_handler import GmailHandler


@pytest.fixture
def handler():
    return GmailHandler()


@pytest.mark.asyncio
async def test_parse_pre_parsed_email(handler):
    """Test parsing pre-parsed email data (from worker after Gmail API fetch)."""
    raw = {
        "from": "alice@example.com",
        "subject": "Password reset help",
        "body": "I need help resetting my password.",
        "thread_id": "thread123",
        "message_id": "msg456",
    }

    result = await handler.parse_inbound(raw)

    assert result.customer_identifier == "alice@example.com"
    assert result.identifier_type.value == "email"
    assert result.channel.value == "email"
    assert result.content == "I need help resetting my password."
    assert result.subject == "Password reset help"
    assert result.metadata["thread_id"] == "thread123"


@pytest.mark.asyncio
async def test_parse_pubsub_notification(handler):
    """Test parsing raw Pub/Sub notification."""
    data = base64.b64encode(json.dumps({
        "emailAddress": "bob@example.com",
        "historyId": 12345,
    }).encode()).decode()

    raw = {
        "message": {
            "data": data,
            "messageId": "pub123",
        },
        "subscription": "projects/test/subscriptions/gmail",
    }

    result = await handler.parse_inbound(raw)

    assert result.customer_identifier == "bob@example.com"
    assert result.channel.value == "email"
    assert result.content == "[Pending Gmail API fetch]"
    assert result.metadata["needs_fetch"] is True


@pytest.mark.asyncio
async def test_format_response_formal(handler):
    """Test formal email response formatting."""
    result = await handler.format_response(
        "Here's how to reset your password.",
        {"customer_name": "Alice", "ticket_number": "TKT-0001"},
    )

    assert "Hi Alice," in result
    assert "Best regards," in result
    assert "TechCorp Support Team" in result
    assert "TKT-0001" in result


@pytest.mark.asyncio
async def test_format_response_max_500_words(handler):
    """Test email response stays under 500 words."""
    long_text = " ".join(["word"] * 600)
    result = await handler.format_response(long_text, {"customer_name": "Test"})
    assert len(result.split()) <= 510


@pytest.mark.asyncio
async def test_parse_invalid_payload_raises(handler):
    """Test that invalid payload raises ValueError."""
    with pytest.raises(ValueError, match="Invalid Gmail webhook payload"):
        await handler.parse_inbound({})
