"""Channel-specific response formatting per brand-voice.md."""


def format_for_email(response: str, customer_name: str = "there",
                     ticket_number: str = "") -> str:
    """Format response for email — formal with greeting and signature, max 500 words."""
    greeting = f"Hi {customer_name},"
    signature = (
        "\n\nBest regards,\n"
        "TechCorp Support Team\n"
        "support@techcorp.io | status.techcorp.io"
    )
    ticket_ref = f"\n\nYour ticket reference: {ticket_number}" if ticket_number else ""

    formatted = f"{greeting}\n\n{response}{ticket_ref}{signature}"

    # Enforce 500-word limit
    words = formatted.split()
    if len(words) > 500:
        formatted = " ".join(words[:497]) + "..." + signature

    return formatted


def format_for_whatsapp(response: str, ticket_number: str = "") -> str:
    """Format response for WhatsApp — conversational, max 1600 chars.

    Returns a list of message strings if splitting is needed.
    """
    ticket_ref = f"\n\nTicket: {ticket_number}" if ticket_number else ""
    full_response = f"{response}{ticket_ref}"

    # If under 1600 chars, return as-is
    if len(full_response) <= 1600:
        return full_response

    # Split at sentence boundaries
    return _split_at_sentences(full_response, max_chars=1600)


def format_for_web(response: str, customer_name: str = "there",
                   ticket_number: str = "") -> str:
    """Format response for web form — semi-formal with ticket reference, max 300 words."""
    greeting = f"Hi {customer_name},"
    ticket_ref = ""
    if ticket_number:
        ticket_ref = (
            f"\n\nYour ticket reference: {ticket_number}\n"
            "Track your ticket at support.techcorp.io"
        )

    formatted = f"{greeting}\n\n{response}{ticket_ref}"

    # Enforce 300-word limit
    words = formatted.split()
    if len(words) > 300:
        formatted = " ".join(words[:297]) + "..." + ticket_ref

    return formatted


def format_response(response: str, channel: str, customer_name: str = "there",
                    ticket_number: str = "") -> str:
    """Route to the appropriate channel formatter."""
    formatters = {
        "email": format_for_email,
        "whatsapp": format_for_whatsapp,
        "web_form": format_for_web,
    }

    formatter = formatters.get(channel, format_for_web)

    if channel == "whatsapp":
        return formatter(response, ticket_number=ticket_number)
    return formatter(response, customer_name=customer_name, ticket_number=ticket_number)


def _split_at_sentences(text: str, max_chars: int = 1600) -> str:
    """Split text at sentence boundaries for WhatsApp multi-message.

    Returns concatenated messages separated by newlines.
    In production, the delivery layer would send these as separate messages.
    """
    sentences = []
    current = ""

    for char in text:
        current += char
        if char in ".!?" and len(current.strip()) > 0:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    messages = []
    current_msg = ""

    for sentence in sentences:
        if len(current_msg) + len(sentence) + 1 <= max_chars:
            current_msg = f"{current_msg} {sentence}".strip()
        else:
            if current_msg:
                messages.append(current_msg)
            current_msg = sentence

    if current_msg:
        messages.append(current_msg)

    return "\n---\n".join(messages) if messages else text
