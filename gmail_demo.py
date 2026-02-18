"""
Gmail Auto-Reply Demo Script
----------------------------
Polls Gmail every 10 seconds for new unread emails and sends an auto-reply.
No Pub/Sub setup needed — works directly with Gmail API + refresh token.

Usage:
    py gmail_demo.py
"""

import base64
import os
import time
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv("production/.env")

CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
WATCH_EMAIL = os.getenv("GMAIL_WATCH_EMAIL", "jameelamazher@gmail.com")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

seen_message_ids = set()


def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def generate_ticket_id():
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TKT-{suffix}"


def get_email_body(payload):
    """Extract plain text body from email payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            # nested parts
            if "parts" in part:
                for subpart in part["parts"]:
                    if subpart["mimeType"] == "text/plain":
                        data = subpart["body"].get("data", "")
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    # single part
    data = payload.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return "(no body)"


def build_reply(sender_name, ticket_id, original_body):
    """Build a professional auto-reply email body."""
    preview = original_body.strip()[:200]
    return f"""Hi {sender_name},

Thank you for reaching out to TechCorp Support!

We have received your message and a ticket has been created for you:

  Ticket ID : {ticket_id}
  Status    : Open
  Priority  : Standard

Your message preview:
"{preview}..."

Our AI support agent has reviewed your request. A detailed response or a human agent will follow up within 1 business hour if needed.

You can check your ticket status at: https://support.techcorp.io/tickets/{ticket_id}

Best regards,
TechCorp Support Team (Digital FTE — 24/7 AI Agent)
support@techcorp.io | status.techcorp.io
"""


def send_reply(service, original_msg, to_email, sender_name, ticket_id, original_body, thread_id):
    """Send a reply in the same Gmail thread."""
    subject = None
    for header in original_msg["payload"]["headers"]:
        if header["name"] == "Subject":
            subject = header["value"]
            break
    reply_subject = subject if subject and subject.startswith("Re:") else f"Re: {subject or 'Support Request'}"

    body_text = build_reply(sender_name, ticket_id, original_body)

    message = MIMEMultipart()
    message["to"] = to_email
    message["from"] = WATCH_EMAIL
    message["subject"] = reply_subject
    message.attach(MIMEText(body_text, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": thread_id},
    ).execute()
    print(f"  ✓ Reply sent to {to_email} | Ticket: {ticket_id}")


def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def poll_inbox(service):
    """Check for new unread emails and auto-reply."""
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=10,
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return

    for msg_ref in messages:
        msg_id = msg_ref["id"]
        if msg_id in seen_message_ids:
            continue

        seen_message_ids.add(msg_id)

        msg = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full",
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        from_header = headers.get("From", "")
        subject = headers.get("Subject", "(no subject)")
        thread_id = msg.get("threadId", msg_id)

        # Parse sender name and email
        if "<" in from_header:
            sender_name = from_header.split("<")[0].strip().strip('"')
            sender_email = from_header.split("<")[1].rstrip(">")
        else:
            sender_email = from_header.strip()
            sender_name = sender_email.split("@")[0]

        body = get_email_body(msg["payload"])
        ticket_id = generate_ticket_id()

        print(f"\n{'='*60}")
        print(f"  New Email Received!")
        print(f"  From    : {from_header}")
        print(f"  Subject : {subject}")
        print(f"  Ticket  : {ticket_id}")
        print(f"{'='*60}")

        send_reply(service, msg, sender_email, sender_name, ticket_id, body, thread_id)
        mark_as_read(service, msg_id)


def main():
    print("=" * 60)
    print("  CRM Digital FTE — Gmail Auto-Reply Demo")
    print(f"  Watching: {WATCH_EMAIL}")
    print("  Polling every 10 seconds... (Ctrl+C to stop)")
    print("=" * 60)

    service = get_gmail_service()
    print("  Gmail API connected successfully!\n")

    # Load already-seen messages on startup (don't reply to old emails)
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX", "UNREAD"], maxResults=50
    ).execute()
    for msg in results.get("messages", []):
        seen_message_ids.add(msg["id"])
    print(f"  Skipping {len(seen_message_ids)} existing unread emails.")
    print("  Waiting for NEW emails...\n")

    while True:
        try:
            poll_inbox(service)
        except Exception as e:
            print(f"  [Error] {e}")
        time.sleep(10)


if __name__ == "__main__":
    main()
