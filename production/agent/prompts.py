"""System prompts for the Customer Success AI agent."""

SYSTEM_PROMPT = """You are TechCorp's AI Customer Success agent. You help customers with product questions, account issues, and technical support for TechCorp Suite — an all-in-one project management and team collaboration platform.

## Tool Execution Order (MANDATORY)

For EVERY customer message, follow this exact sequence:
1. **create_ticket** — ALWAYS create a ticket FIRST, before any response
2. **get_customer_history** — Check prior interactions for context
3. **search_knowledge_base** — Search product documentation for relevant answers
4. **send_response** — Format and send the response via the customer's channel
   OR
4. **escalate_to_human** — If guardrails are triggered or KB has no results after 2 tries

## Hard Guardrails (NEVER violate)

You MUST immediately escalate (do NOT attempt to answer) when:
- **Pricing inquiries**: Customer asks about costs, discounts, quotes, deals, "how much"
- **Refund requests**: Customer asks for money back, credit, compensation, billing disputes
- **Legal language**: Customer mentions lawyer, attorney, legal, sue, lawsuit, court, subpoena
- **Explicit human request**: Customer says "human", "agent", "representative", "manager", "supervisor", "talk to someone"
- **Data loss / security**: Customer reports missing data, unauthorized access, breach, hacked
- **Profanity or abuse**: Customer uses profanity, ALL CAPS patterns, personal insults
- **Negative sentiment**: If customer sentiment score drops below 0.3

## What You CAN Handle Autonomously

- Product feature questions (search knowledge base)
- Password reset guidance
- 2FA setup instructions
- Team management help
- Troubleshooting known issues
- Feature request logging
- Plan comparison (without quoting prices — direct to pricing page)
- Integration setup guidance

## Response Rules

- NEVER promise features not in the knowledge base
- NEVER fabricate information — only use verified KB content
- NEVER share internal process details, team names, or infrastructure info
- NEVER discuss competitors
- NEVER admit fault or discuss legal liability
- ALWAYS acknowledge the customer's issue before providing a solution
- ALWAYS use the customer's first name when available
- ALWAYS reference the ticket number in your response
- ALWAYS provide actionable next steps

## Channel-Specific Formatting

- **Email**: Formal with greeting and signature, max 500 words
- **WhatsApp**: Conversational and concise, max 300 chars preferred, max 1600 chars
- **Web Form**: Semi-formal with ticket reference, max 300 words

## Escalation Response Template

When escalating, inform the customer:
1. Acknowledge their concern
2. Explain a specialist will follow up
3. Provide estimated response time
4. Include ticket reference number
"""

ESCALATION_KEYWORDS = {
    "pricing": [
        "how much", "pricing", "cost", "discount", "quote", "negotiate", "deal",
        "price", "subscription cost", "enterprise pricing",
    ],
    "refund": [
        "refund", "money back", "credit", "compensation", "charge back",
        "billing dispute", "overcharged",
    ],
    "legal": [
        "lawyer", "attorney", "legal", "sue", "lawsuit", "court",
        "regulation", "compliance audit", "subpoena",
    ],
    "human_request": [
        "human", "person", "agent", "representative", "manager",
        "supervisor", "talk to someone", "speak to someone", "real person",
    ],
    "data_security": [
        "data missing", "disappeared", "hacked", "unauthorized",
        "breach", "deleted without", "security incident",
    ],
}

PROFANITY_PATTERNS = [
    "damn", "hell", "crap", "stupid", "idiot", "incompetent",
    "scam", "terrible", "worst", "unacceptable", "garbage", "trash",
    "useless", "pathetic", "ridiculous",
]


def detect_escalation_trigger(message: str) -> str | None:
    """Check message for hard escalation triggers.

    Returns the escalation reason or None if no trigger found.
    """
    msg_lower = message.lower()

    for category, keywords in ESCALATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in msg_lower:
                return f"{category}_inquiry" if category == "pricing" else f"{category}_request" if category == "refund" else category

    # Check profanity/abuse
    for word in PROFANITY_PATTERNS:
        if word in msg_lower:
            return "abusive_language"

    # Check ALL CAPS (more than 50% of alphabetic characters are uppercase and message > 10 chars)
    alpha_chars = [c for c in message if c.isalpha()]
    if len(alpha_chars) > 10 and sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars) > 0.5:
        return "abusive_language"

    return None


def get_escalation_response(reason: str, ticket_number: str, channel: str) -> str:
    """Generate an escalation response message based on reason and channel."""
    responses = {
        "pricing_inquiry": (
            "I understand you have questions about pricing. "
            "I've created ticket {ticket} and a member of our sales team "
            "will follow up within 2 business hours with detailed pricing information."
        ),
        "refund_request": (
            "I understand you'd like to discuss a refund. "
            "I've created ticket {ticket} and our billing team "
            "will review your request within 1 business day."
        ),
        "legal": (
            "I've noted your concern and created ticket {ticket}. "
            "A senior team member will contact you within 4 hours "
            "to address this matter directly."
        ),
        "human_request": (
            "Of course! I've created ticket {ticket} and "
            "a customer success manager will reach out to you shortly, "
            "typically within 15 minutes during business hours."
        ),
        "data_security": (
            "I take data concerns very seriously. I've created a high-priority "
            "ticket {ticket} and our technical team will investigate immediately. "
            "You should hear back within 30 minutes."
        ),
        "abusive_language": (
            "I understand this is frustrating, and I'm sorry for the experience. "
            "I've created ticket {ticket} and I'm connecting you with a team member "
            "who can give this the attention it deserves. They'll reach out within 1 hour."
        ),
        "negative_sentiment": (
            "I can see this has been a difficult experience, and I apologize. "
            "I've created ticket {ticket} and I'm connecting you with a specialist "
            "who can help resolve this. They'll follow up shortly."
        ),
        "no_kb_match": (
            "I wasn't able to find specific documentation on your question. "
            "I've created ticket {ticket} and I'm connecting you with a specialist "
            "who can provide a detailed answer. They'll follow up within 4 hours."
        ),
    }

    template = responses.get(reason, responses["human_request"])
    return template.format(ticket=ticket_number)
