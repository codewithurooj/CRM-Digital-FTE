"""Unit tests for agent tools — test each @function_tool with mocked DB."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from production.tests.conftest import make_mock_pool


@pytest.mark.asyncio
async def test_check_guardrails_pricing():
    """Test guardrail detection for pricing keywords."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("How much does the enterprise plan cost?")
    assert result is not None
    assert result["should_escalate"] is True
    assert "pricing" in result["reason"]


@pytest.mark.asyncio
async def test_check_guardrails_refund():
    """Test guardrail detection for refund keywords."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("I need a refund for last month")
    assert result is not None
    assert result["should_escalate"] is True
    assert "refund" in result["reason"]


@pytest.mark.asyncio
async def test_check_guardrails_legal():
    """Test guardrail detection for legal keywords."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("I'm going to contact my lawyer about this")
    assert result is not None
    assert result["should_escalate"] is True
    assert result["reason"] == "legal"


@pytest.mark.asyncio
async def test_check_guardrails_human_request():
    """Test guardrail detection for human request."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("I want to talk to a human agent")
    assert result is not None
    assert result["should_escalate"] is True


@pytest.mark.asyncio
async def test_check_guardrails_negative_sentiment():
    """Test guardrail detection for negative sentiment."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("I have a normal question", sentiment_score=0.2)
    assert result is not None
    assert result["should_escalate"] is True
    assert result["reason"] == "negative_sentiment"


@pytest.mark.asyncio
async def test_check_guardrails_no_trigger():
    """Test guardrails pass for normal messages."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("How do I reset my password?")
    assert result is None


@pytest.mark.asyncio
async def test_check_guardrails_all_caps():
    """Test guardrail detection for ALL CAPS abuse."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("THIS IS COMPLETELY BROKEN AND NOTHING WORKS")
    assert result is not None
    assert result["should_escalate"] is True
    assert result["reason"] == "abusive_language"


@pytest.mark.asyncio
async def test_check_guardrails_profanity():
    """Test guardrail detection for profanity."""
    from production.agent.tools import check_guardrails

    result = check_guardrails("This service is terrible and incompetent")
    assert result is not None
    assert result["should_escalate"] is True
    assert result["reason"] == "abusive_language"
