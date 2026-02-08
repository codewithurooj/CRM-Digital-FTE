"""Unit tests for channel-specific formatting — same content, different format per channel."""
import pytest

from production.agent.formatters import format_response


class TestSameContentDifferentFormat:
    """Verify same question gets different formatting per channel."""

    RESPONSE = "To reset your password, go to app.techcorp.io/login and click Forgot Password."

    def test_email_is_formal(self):
        result = format_response(self.RESPONSE, channel="email", customer_name="Alice", ticket_number="TKT-0001")
        assert "Hi Alice," in result
        assert "Best regards," in result
        assert "TechCorp Support Team" in result
        assert "TKT-0001" in result

    def test_whatsapp_is_concise(self):
        result = format_response(self.RESPONSE, channel="whatsapp", ticket_number="TKT-0001")
        assert "Best regards," not in result
        assert "TKT-0001" in result
        assert len(result) <= 1600

    def test_web_is_semi_formal(self):
        result = format_response(self.RESPONSE, channel="web_form", customer_name="Alice", ticket_number="TKT-0001")
        assert "Hi Alice," in result
        assert "Best regards," not in result
        assert "support.techcorp.io" in result

    def test_email_longer_than_whatsapp(self):
        email = format_response(self.RESPONSE, channel="email", customer_name="Alice")
        whatsapp = format_response(self.RESPONSE, channel="whatsapp")
        assert len(email) > len(whatsapp)

    def test_whatsapp_splits_at_sentences(self):
        long_response = ". ".join(["This is a detailed step for the process"] * 50)
        result = format_response(long_response, channel="whatsapp")
        if len(long_response) > 1600:
            segments = result.split("\n---\n")
            for seg in segments:
                assert len(seg) <= 1600
