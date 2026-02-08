"""Unit tests for system prompts — verify guardrail rules and tool instructions are present."""
import pytest

from production.agent.prompts import SYSTEM_PROMPT, ESCALATION_KEYWORDS, PROFANITY_PATTERNS


class TestSystemPrompt:
    """Verify system prompt contains required instructions."""

    def test_contains_tool_order(self):
        assert "create_ticket" in SYSTEM_PROMPT
        assert "get_customer_history" in SYSTEM_PROMPT
        assert "search_knowledge_base" in SYSTEM_PROMPT
        assert "send_response" in SYSTEM_PROMPT
        assert "escalate_to_human" in SYSTEM_PROMPT

    def test_contains_guardrail_rules(self):
        assert "Pricing" in SYSTEM_PROMPT
        assert "Refund" in SYSTEM_PROMPT
        assert "Legal" in SYSTEM_PROMPT
        assert "human" in SYSTEM_PROMPT.lower()

    def test_contains_channel_formatting(self):
        assert "Email" in SYSTEM_PROMPT
        assert "WhatsApp" in SYSTEM_PROMPT
        assert "Web Form" in SYSTEM_PROMPT

    def test_enforces_ticket_first(self):
        assert "ALWAYS" in SYSTEM_PROMPT
        assert "first" in SYSTEM_PROMPT.lower()

    def test_forbids_fabrication(self):
        assert "NEVER" in SYSTEM_PROMPT
        assert "fabricate" in SYSTEM_PROMPT.lower() or "promise" in SYSTEM_PROMPT.lower()


class TestEscalationKeywords:
    def test_pricing_keywords_exist(self):
        assert "pricing" in ESCALATION_KEYWORDS
        assert len(ESCALATION_KEYWORDS["pricing"]) >= 5

    def test_refund_keywords_exist(self):
        assert "refund" in ESCALATION_KEYWORDS
        assert len(ESCALATION_KEYWORDS["refund"]) >= 4

    def test_legal_keywords_exist(self):
        assert "legal" in ESCALATION_KEYWORDS
        assert "lawyer" in ESCALATION_KEYWORDS["legal"]

    def test_human_request_keywords_exist(self):
        assert "human_request" in ESCALATION_KEYWORDS
        assert "human" in ESCALATION_KEYWORDS["human_request"]


class TestProfanityPatterns:
    def test_profanity_list_not_empty(self):
        assert len(PROFANITY_PATTERNS) > 0

    def test_contains_known_patterns(self):
        assert "terrible" in PROFANITY_PATTERNS
        assert "incompetent" in PROFANITY_PATTERNS
