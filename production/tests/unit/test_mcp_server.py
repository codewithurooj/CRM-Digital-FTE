"""Unit tests for standalone MCP server exposing 5 agent tools (FR-046)."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestMCPServerDefinition:
    """Tests that the MCP server is properly configured."""

    def test_mcp_server_instance_exists(self):
        """MCP server instance is created with correct name."""
        from production.mcp_server import mcp
        assert mcp.name == "CRM Digital FTE"

    @pytest.mark.asyncio
    async def test_all_five_tools_registered(self):
        """All 5 agent tools are registered on the MCP server."""
        from production.mcp_server import mcp
        # FastMCP stores tools internally; verify by listing them
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "search_knowledge_base" in tool_names
        assert "create_ticket" in tool_names
        assert "get_customer_history" in tool_names
        assert "escalate_to_human" in tool_names
        assert "send_response" in tool_names


class TestSearchKnowledgeBaseTool:
    """Tests for the search_knowledge_base MCP tool."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        from production.mcp_server import mcp_search_knowledge_base

        mock_results = [
            {"title": "Password Reset", "content": "Go to settings...", "category": "account"},
        ]

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.knowledge_base.get_by_category", new_callable=AsyncMock, return_value=mock_results):
            mock_pool.return_value = MagicMock()
            result = await mcp_search_knowledge_base(query="password reset", category="account")

        parsed = json.loads(result)
        assert parsed["total"] >= 1
        assert parsed["results"][0]["title"] == "Password Reset"

    @pytest.mark.asyncio
    async def test_search_no_results(self):
        from production.mcp_server import mcp_search_knowledge_base

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.knowledge_base.get_by_category", new_callable=AsyncMock, return_value=[]):
            mock_pool.return_value = MagicMock()
            result = await mcp_search_knowledge_base(query="nonexistent", category="")

        parsed = json.loads(result)
        assert parsed["total"] == 0


class TestCreateTicketTool:
    """Tests for the create_ticket MCP tool."""

    @pytest.mark.asyncio
    async def test_create_ticket_success(self):
        from production.mcp_server import mcp_create_ticket

        mock_ticket = {"id": "tkt-1", "ticket_number": "TKT-0001", "status": "open"}

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.tickets.create_ticket", new_callable=AsyncMock, return_value=mock_ticket):
            mock_pool.return_value = MagicMock()
            result = await mcp_create_ticket(
                customer_id="cust-1",
                subject="Need help",
                category="technical",
                source_channel="web_form",
                priority="medium",
            )

        parsed = json.loads(result)
        assert parsed["ticket_number"] == "TKT-0001"
        assert parsed["status"] == "open"

    @pytest.mark.asyncio
    async def test_create_ticket_failure(self):
        from production.mcp_server import mcp_create_ticket

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.tickets.create_ticket", new_callable=AsyncMock, return_value=None):
            mock_pool.return_value = MagicMock()
            result = await mcp_create_ticket(
                customer_id="cust-1",
                subject="Need help",
                category="technical",
                source_channel="web_form",
            )

        parsed = json.loads(result)
        assert "error" in parsed


class TestGetCustomerHistoryTool:
    """Tests for the get_customer_history MCP tool."""

    @pytest.mark.asyncio
    async def test_returns_history(self):
        from production.mcp_server import mcp_get_customer_history

        mock_messages = [
            {"channel": "email", "direction": "inbound", "role": "customer", "content": "Hello", "created_at": "2026-01-01"},
        ]

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.messages.get_customer_history", new_callable=AsyncMock, return_value=mock_messages):
            mock_pool.return_value = MagicMock()
            result = await mcp_get_customer_history(customer_id="cust-1", limit=10)

        parsed = json.loads(result)
        assert parsed["total"] == 1
        assert parsed["messages"][0]["channel"] == "email"

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_history(self):
        from production.mcp_server import mcp_get_customer_history

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.messages.get_customer_history", new_callable=AsyncMock, return_value=[]):
            mock_pool.return_value = MagicMock()
            result = await mcp_get_customer_history(customer_id="cust-1")

        parsed = json.loads(result)
        assert parsed["total"] == 0


class TestEscalateToHumanTool:
    """Tests for the escalate_to_human MCP tool."""

    @pytest.mark.asyncio
    async def test_escalation_success(self):
        from production.mcp_server import mcp_escalate_to_human

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.tickets.update_ticket_status", new_callable=AsyncMock), \
             patch("production.database.queries.conversations.update_status", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock):
            mock_pool.return_value = MagicMock()
            result = await mcp_escalate_to_human(
                customer_id="cust-1",
                ticket_id="tkt-1",
                reason="pricing_inquiry",
                conversation_id="conv-1",
            )

        parsed = json.loads(result)
        assert parsed["status"] == "escalated"
        assert parsed["reason"] == "pricing_inquiry"


class TestSendResponseTool:
    """Tests for the send_response MCP tool."""

    @pytest.mark.asyncio
    async def test_send_response_success(self):
        from production.mcp_server import mcp_send_response

        with patch("production.database.pool.get_pool", new_callable=AsyncMock) as mock_pool, \
             patch("production.database.queries.messages.store_message", new_callable=AsyncMock), \
             patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock):
            mock_pool.return_value = MagicMock()
            result = await mcp_send_response(
                customer_id="cust-1",
                conversation_id="conv-1",
                channel="web_form",
                response_text="Here is your answer.",
                ticket_number="TKT-0001",
                customer_name="Alice",
            )

        parsed = json.loads(result)
        assert parsed["status"] == "sent"
        assert parsed["channel"] == "web_form"
