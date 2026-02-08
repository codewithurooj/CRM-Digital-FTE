"""Unit tests for WhatsApp channel handler — parse, format, and signature validation."""
import pytest

from production.channels.whatsapp_handler import WhatsAppHandler, validate_twilio_signature


@pytest.fixture
def handler():
    return WhatsAppHandler()


@pytest.mark.asyncio
async def test_parse_inbound(handler):
    """Test parsing Twilio webhook form-encoded data."""
    raw = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+14155238886",
        "Body": "How do I reset my password?",
        "MessageSid": "SM123",
        "AccountSid": "AC456",
        "ProfileName": "John Doe",
        "NumMedia": "0",
    }

    result = await handler.parse_inbound(raw)

    assert result.customer_identifier == "+1234567890"
    assert result.identifier_type.value == "phone"
    assert result.channel.value == "whatsapp"
    assert result.content == "How do I reset my password?"
    assert result.metadata["profile_name"] == "John Doe"
    assert result.metadata["message_sid"] == "SM123"


@pytest.mark.asyncio
async def test_parse_empty_body(handler):
    """Test parsing message with empty body (media-only)."""
    raw = {"From": "whatsapp:+1234567890", "Body": "", "NumMedia": "1"}

    result = await handler.parse_inbound(raw)
    assert "text only supported" in result.content.lower()


@pytest.mark.asyncio
async def test_format_response_short(handler):
    """Test short WhatsApp response stays concise."""
    result = await handler.format_response(
        "Reset at app.techcorp.io/login > Forgot Password.",
        {"ticket_number": "TKT-0001"},
    )

    assert "TKT-0001" in result
    assert len(result) < 1600


@pytest.mark.asyncio
async def test_format_response_splits_long(handler):
    """Test long WhatsApp response is split at sentence boundaries."""
    long_text = ". ".join(["This is a fairly long sentence with details"] * 50)
    result = await handler.format_response(long_text, {})

    # Should contain split markers if message was too long
    if len(long_text) > 1600:
        assert "---" in result or len(result) <= 1600


def test_validate_twilio_signature():
    """Test Twilio signature validation."""
    import hashlib
    import hmac
    import base64

    auth_token = "test_token_123"
    url = "https://example.com/webhooks/whatsapp"
    params = {"Body": "Hello", "From": "whatsapp:+1234567890"}

    # Compute expected signature
    sorted_params = sorted(params.items())
    data_string = url + "".join(f"{k}{v}" for k, v in sorted_params)
    computed = hmac.new(
        auth_token.encode("utf-8"),
        data_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    valid_signature = base64.b64encode(computed).decode("utf-8")

    assert validate_twilio_signature(url, params, valid_signature, auth_token) is True
    assert validate_twilio_signature(url, params, "invalid_sig", auth_token) is False
