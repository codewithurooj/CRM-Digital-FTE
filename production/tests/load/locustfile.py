"""Locust load test — simulate 100+ web forms, 50+ emails, 50+ WhatsApp messages."""
import base64
import json
import random

from locust import HttpUser, task, between


class WebFormUser(HttpUser):
    """Simulates web form submissions."""
    wait_time = between(1, 5)
    weight = 5  # 5x more web form traffic

    @task
    def submit_form(self):
        categories = ["account_access", "billing", "technical", "how_to", "feature_request"]
        priorities = ["low", "medium", "high"]
        user_id = random.randint(1, 1000)

        self.client.post("/api/v1/support/form", json={
            "name": f"Load Test User {user_id}",
            "email": f"loadtest{user_id}@example.com",
            "subject": f"Load test question #{random.randint(1, 10000)}",
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "message": "This is a load test message. I need help with my account settings and configuration options.",
        })

    @task(1)
    def check_health(self):
        self.client.get("/api/v1/health")

    @task(1)
    def check_metrics(self):
        self.client.get("/api/v1/metrics/channels")


class GmailWebhookUser(HttpUser):
    """Simulates Gmail Pub/Sub notifications."""
    wait_time = between(2, 10)
    weight = 2

    @task
    def send_gmail_notification(self):
        user_id = random.randint(1, 500)
        data = base64.b64encode(json.dumps({
            "emailAddress": f"gmail_loadtest{user_id}@example.com",
            "historyId": random.randint(10000, 99999),
        }).encode()).decode()

        self.client.post("/api/v1/webhooks/gmail", json={
            "message": {"data": data, "messageId": f"pub-{random.randint(1, 99999)}"},
            "subscription": "projects/techcorp/subscriptions/gmail-push",
        })


class WhatsAppWebhookUser(HttpUser):
    """Simulates Twilio WhatsApp webhooks."""
    wait_time = between(2, 10)
    weight = 2

    @task
    def send_whatsapp_message(self):
        phone = f"+1{random.randint(2000000000, 9999999999)}"
        questions = [
            "How do I reset my password?",
            "Can you help me set up 2FA?",
            "My tasks are not syncing",
            "How do I export my data?",
            "human",
        ]

        self.client.post("/api/v1/webhooks/whatsapp", data={
            "From": f"whatsapp:{phone}",
            "To": "whatsapp:+14155238886",
            "Body": random.choice(questions),
            "MessageSid": f"SM{random.randint(100000, 999999)}",
            "AccountSid": "AC_loadtest",
            "ProfileName": f"User {phone[-4:]}",
            "NumMedia": "0",
        })
