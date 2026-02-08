"""Unit tests for response formatters — email, WhatsApp, web form."""
import pytest

from production.agent.formatters import (
    format_for_email,
    format_for_whatsapp,
    format_for_web,
    format_response,
)


class TestEmailFormatter:
    def test_includes_greeting(self):
        result = format_for_email("Your answer.", customer_name="Alice")
        assert "Hi Alice," in result

    def test_includes_signature(self):
        result = format_for_email("Your answer.", customer_name="Alice")
        assert "Best regards," in result
        assert "TechCorp Support Team" in result

    def test_includes_ticket_reference(self):
        result = format_for_email("Answer.", ticket_number="TKT-0001")
        assert "TKT-0001" in result

    def test_max_500_words(self):
        long_text = " ".join(["word"] * 600)
        result = format_for_email(long_text)
        assert len(result.split()) <= 510  # Allow buffer for greeting/signature

    def test_default_name(self):
        result = format_for_email("Answer.")
        assert "Hi there," in result


class TestWhatsAppFormatter:
    def test_short_message_unchanged(self):
        result = format_for_whatsapp("Short answer.")
        assert result == "Short answer."

    def test_includes_ticket_ref(self):
        result = format_for_whatsapp("Answer.", ticket_number="TKT-0001")
        assert "TKT-0001" in result

    def test_splits_long_message(self):
        long_text = ". ".join(["This is a sentence"] * 100)
        result = format_for_whatsapp(long_text)
        # Should contain split markers
        assert len(result) > 0

    def test_max_1600_chars_per_segment(self):
        long_text = ". ".join(["This is a sentence"] * 100)
        result = format_for_whatsapp(long_text)
        segments = result.split("\n---\n")
        for segment in segments:
            assert len(segment) <= 1600


class TestWebFormatter:
    def test_includes_greeting(self):
        result = format_for_web("Your answer.", customer_name="Bob")
        assert "Hi Bob," in result

    def test_includes_ticket_reference(self):
        result = format_for_web("Answer.", ticket_number="TKT-0002")
        assert "TKT-0002" in result
        assert "support.techcorp.io" in result

    def test_max_300_words(self):
        long_text = " ".join(["word"] * 400)
        result = format_for_web(long_text)
        assert len(result.split()) <= 310  # Allow buffer


class TestFormatResponse:
    def test_routes_to_email(self):
        result = format_response("Answer.", channel="email", customer_name="Alice")
        assert "Best regards," in result

    def test_routes_to_whatsapp(self):
        result = format_response("Answer.", channel="whatsapp")
        assert "Best regards," not in result

    def test_routes_to_web(self):
        result = format_response("Answer.", channel="web_form", customer_name="Bob")
        assert "Hi Bob," in result

    def test_unknown_channel_defaults_to_web(self):
        result = format_response("Answer.", channel="unknown", customer_name="Eve")
        assert "Hi Eve," in result
