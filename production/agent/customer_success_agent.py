"""Customer Success AI Agent — OpenAI Agents SDK orchestration."""
import json
import logging
from datetime import datetime, timezone

from agents import Agent, Runner

from production.agent.prompts import SYSTEM_PROMPT, detect_escalation_trigger, get_escalation_response
from production.agent.tools import (
    create_ticket,
    get_customer_history,
    search_knowledge_base,
    escalate_to_human,
    send_response,
    check_guardrails,
)
from production.agent.formatters import format_response

logger = logging.getLogger(__name__)

# Agent definition using OpenAI Agents SDK
customer_success_agent = Agent(
    name="TechCorp Customer Success Agent",
    instructions=SYSTEM_PROMPT,
    tools=[
        create_ticket,
        get_customer_history,
        search_knowledge_base,
        escalate_to_human,
        send_response,
    ],
)


async def process_message(
    customer_id: str,
    conversation_id: str,
    channel: str,
    message: str,
    customer_name: str = "",
    sentiment_score: float = 0.5,
) -> dict:
    """Process a customer message through the AI agent.

    This is the main entry point for the agent pipeline. It:
    1. Checks guardrails (immediate escalation if triggered)
    2. Runs the agent with conversation context
    3. Returns the result including any tool calls made

    Args:
        customer_id: UUID of the customer
        conversation_id: UUID of the conversation
        channel: Source channel (email, whatsapp, web_form)
        message: Customer's message content
        customer_name: Customer's first name
        sentiment_score: Sentiment score (0-1, default 0.5)

    Returns:
        dict with keys: status, response, ticket_number, escalated, reason
    """
    result = {
        "status": "success",
        "response": "",
        "ticket_number": "",
        "escalated": False,
        "reason": None,
        "channel": channel,
    }

    try:
        # Step 1: Check guardrails before running agent
        guardrail_check = check_guardrails(message, sentiment_score)

        if guardrail_check and guardrail_check.get("should_escalate"):
            result = await _handle_escalation(
                customer_id=customer_id,
                conversation_id=conversation_id,
                channel=channel,
                message=message,
                reason=guardrail_check["reason"],
                customer_name=customer_name,
            )
            return result

        # Step 2: Run the agent
        context_message = _build_context(
            customer_id=customer_id,
            conversation_id=conversation_id,
            channel=channel,
            customer_name=customer_name,
        )

        run_result = await Runner.run(
            customer_success_agent,
            input=f"{context_message}\n\nCustomer message: {message}",
        )

        # Extract the final output
        result["response"] = run_result.final_output if run_result.final_output else ""
        result["status"] = "success"

        logger.info(
            "Agent processed message",
            extra={
                "customer_id": customer_id,
                "channel": channel,
                "escalated": result["escalated"],
            },
        )

    except Exception as e:
        logger.error(f"Agent processing error: {e}", exc_info=True)
        result["status"] = "error"
        result["response"] = _get_fallback_response(channel, customer_name)

    return result


async def _handle_escalation(
    customer_id: str,
    conversation_id: str,
    channel: str,
    message: str,
    reason: str,
    customer_name: str = "",
) -> dict:
    """Handle an escalation triggered by guardrails."""
    from production.database.pool import get_pool
    from production.database.queries import tickets, conversations, messages, metrics

    pool = await get_pool()

    # Create ticket first
    ticket = await tickets.create_ticket(
        pool,
        customer_id=customer_id,
        subject=f"Escalation: {reason}",
        category="complaint" if "abuse" in reason else "billing" if "refund" in reason or "pricing" in reason else "technical",
        source_channel=channel,
        priority="high",
        conversation_id=conversation_id or None,
    )

    ticket_number = ticket["ticket_number"] if ticket else "PENDING"

    # Update ticket to escalated
    if ticket:
        await tickets.update_ticket_status(
            pool, ticket["id"], "escalated",
            escalation_reason=reason,
        )

    # Update conversation
    if conversation_id:
        await conversations.update_status(
            pool, conversation_id, "escalated",
            escalation_reason=reason,
        )

    # Generate escalation response
    response_text = get_escalation_response(reason, ticket_number, channel)
    formatted = format_response(response_text, channel, customer_name or "there", ticket_number)

    # Store outbound message
    await messages.store_message(
        pool,
        conversation_id=conversation_id,
        customer_id=customer_id,
        channel=channel,
        direction="outbound",
        role="agent",
        content=formatted,
        metadata={"escalation_reason": reason, "ticket_number": ticket_number},
    )

    # Record metrics
    await metrics.record_metric(
        pool, "escalation", 1.0, channel=channel,
        metadata={"reason": reason, "customer_id": customer_id},
    )

    return {
        "status": "escalated",
        "response": formatted,
        "ticket_number": ticket_number,
        "escalated": True,
        "reason": reason,
        "channel": channel,
    }


def _build_context(
    customer_id: str,
    conversation_id: str,
    channel: str,
    customer_name: str = "",
) -> str:
    """Build context string for the agent."""
    return (
        f"Context: customer_id={customer_id}, "
        f"conversation_id={conversation_id}, "
        f"channel={channel}, "
        f"customer_name={customer_name or 'Unknown'}"
    )


def _get_fallback_response(channel: str, customer_name: str = "") -> str:
    """Return a safe fallback response when the agent fails."""
    base = (
        "We're experiencing high demand right now and I wasn't able to fully process "
        "your request. A member of our team will follow up with you shortly. "
        "We apologize for the inconvenience."
    )
    return format_response(base, channel, customer_name or "there")
