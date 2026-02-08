"""Unit tests for web form channel handler — parse and format."""
import pytest

from production.channels.web_form_handler import WebFormHandler


@pytest.fixture
def handler():
    return WebFormHandler()


@pytest.mark.asyncio
async def test_parse_inbound(handler):
    """Test parsing web form data into InboundMessage."""
    raw = {
        "email": "lisa@example.com",
        "message": "How do I set up automations?",
        "subject": "Automation help",
        "name": "Lisa",
        "category": "how_to",
        "priority": "medium",
    }

    result = await handler.parse_inbound(raw)

    assert result.customer_identifier == "lisa@example.com"
    assert result.identifier_type.value == "email"
    assert result.channel.value == "web_form"
    assert result.content == "How do I set up automations?"
    assert result.subject == "Automation help"
    assert result.metadata["name"] == "Lisa"


@pytest.mark.asyncio
async def test_format_response(handler):
    """Test semi-formal response formatting."""
    result = await handler.format_response(
        "Here's how to set up automations.",
        {"customer_name": "Lisa", "ticket_number": "TKT-0001"},
    )

    assert "Hi Lisa," in result
    assert "TKT-0001" in result
    assert "support.techcorp.io" in result


@pytest.mark.asyncio
async def test_deliver_returns_true(handler):
    """Web form deliver is a no-op (responses stored in DB)."""
    result = await handler.deliver("text", "dest", {})
    assert result is True
