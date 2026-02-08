"""Unit tests for guardrails — pricing/refund/legal/human triggers must escalate."""
import pytest

from production.agent.prompts import detect_escalation_trigger, get_escalation_response


class TestDetectEscalationTrigger:
    """Test that all hard escalation triggers are detected."""

    @pytest.mark.parametrize("message,expected_trigger", [
        ("How much does the enterprise plan cost?", "pricing_inquiry"),
        ("What's the pricing for 100 users?", "pricing_inquiry"),
        ("Can I get a discount?", "pricing_inquiry"),
        ("I need a custom quote", "pricing_inquiry"),
    ])
    def test_pricing_triggers(self, message, expected_trigger):
        result = detect_escalation_trigger(message)
        assert result == expected_trigger

    @pytest.mark.parametrize("message,expected_trigger", [
        ("I need a refund for last month", "refund_request"),
        ("Give me my money back", "refund_request"),
        ("I want compensation for the downtime", "refund_request"),
        ("There's a billing dispute", "refund_request"),
    ])
    def test_refund_triggers(self, message, expected_trigger):
        result = detect_escalation_trigger(message)
        assert result == expected_trigger

    @pytest.mark.parametrize("message", [
        "I'm going to sue your company",
        "I'll contact my lawyer",
        "My attorney will be reaching out",
        "I'll take legal action",
        "This is a compliance audit question",
    ])
    def test_legal_triggers(self, message):
        result = detect_escalation_trigger(message)
        assert result == "legal"

    @pytest.mark.parametrize("message", [
        "I want to speak to a human",
        "Connect me to an agent",
        "I need a representative",
        "Let me talk to someone real",
        "I need to speak to a manager",
    ])
    def test_human_request_triggers(self, message):
        result = detect_escalation_trigger(message)
        assert result is not None

    @pytest.mark.parametrize("message", [
        "All my data missing from the project",
        "I think my account was hacked",
        "There's an unauthorized access attempt",
    ])
    def test_data_security_triggers(self, message):
        result = detect_escalation_trigger(message)
        assert result == "data_security"

    @pytest.mark.parametrize("message", [
        "This service is terrible",
        "Your product is the worst",
        "This is unacceptable",
    ])
    def test_profanity_triggers(self, message):
        result = detect_escalation_trigger(message)
        assert result == "abusive_language"

    def test_all_caps_trigger(self):
        result = detect_escalation_trigger("WHY IS EVERYTHING BROKEN")
        assert result == "abusive_language"

    @pytest.mark.parametrize("message", [
        "How do I reset my password?",
        "Can you help me set up 2FA?",
        "Where can I find the API documentation?",
        "I need help connecting Slack",
    ])
    def test_no_trigger_for_normal_messages(self, message):
        result = detect_escalation_trigger(message)
        assert result is None


class TestGetEscalationResponse:
    """Test escalation response generation."""

    def test_pricing_response(self):
        result = get_escalation_response("pricing_inquiry", "TKT-0001", "email")
        assert "TKT-0001" in result
        assert "sales" in result.lower()

    def test_refund_response(self):
        result = get_escalation_response("refund_request", "TKT-0002", "whatsapp")
        assert "TKT-0002" in result
        assert "billing" in result.lower()

    def test_legal_response(self):
        result = get_escalation_response("legal", "TKT-0003", "email")
        assert "TKT-0003" in result
        assert "senior" in result.lower()

    def test_human_request_response(self):
        result = get_escalation_response("human_request", "TKT-0004", "whatsapp")
        assert "TKT-0004" in result

    def test_unknown_reason_uses_default(self):
        result = get_escalation_response("unknown_reason", "TKT-0005", "web_form")
        assert "TKT-0005" in result
