"""AI Agent module — OpenAI Agents SDK with 5 function tools."""
from production.agent.customer_success_agent import process_message, customer_success_agent
from production.agent.formatters import format_response
from production.agent.prompts import detect_escalation_trigger, get_escalation_response
from production.agent.tools import check_guardrails

__all__ = [
    "process_message",
    "customer_success_agent",
    "format_response",
    "detect_escalation_trigger",
    "get_escalation_response",
    "check_guardrails",
]
