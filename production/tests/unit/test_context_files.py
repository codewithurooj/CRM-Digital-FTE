"""Unit tests for context files — T005 TDD target."""
import json
import pathlib

import pytest

CONTEXT_DIR = pathlib.Path(__file__).resolve().parents[2] / "context"


class TestContextFiles:
    """Verify all context files exist and are valid."""

    @pytest.mark.parametrize("filename", [
        "company-profile.md",
        "product-docs.md",
        "escalation-rules.md",
        "brand-voice.md",
    ])
    def test_markdown_files_exist_and_nonempty(self, filename):
        filepath = CONTEXT_DIR / filename
        assert filepath.exists(), f"Missing context file: {filename}"
        content = filepath.read_text(encoding="utf-8")
        assert len(content.strip()) > 50, f"Context file too short: {filename}"

    def test_sample_tickets_valid_json(self):
        filepath = CONTEXT_DIR / "sample-tickets.json"
        assert filepath.exists(), "Missing sample-tickets.json"
        content = filepath.read_text(encoding="utf-8")
        data = json.loads(content)
        # Accept both list format and dict-with-tickets-key format
        tickets = data if isinstance(data, list) else data.get("tickets", [])
        assert len(tickets) >= 5, "Need at least 5 sample tickets"

    def test_sample_tickets_have_required_fields(self):
        filepath = CONTEXT_DIR / "sample-tickets.json"
        data = json.loads(filepath.read_text(encoding="utf-8"))
        tickets = data if isinstance(data, list) else data.get("tickets", [])
        required = {"channel", "subject", "category"}
        for i, ticket in enumerate(tickets):
            missing = required - set(ticket.keys())
            assert not missing, f"Ticket {i} missing fields: {missing}"
            # Must have either 'message' or 'content' for body
            assert "message" in ticket or "content" in ticket, (
                f"Ticket {i} missing message/content body"
            )
