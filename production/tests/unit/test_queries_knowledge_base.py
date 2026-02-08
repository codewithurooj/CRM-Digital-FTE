"""Unit tests for knowledge base queries — T017 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestKnowledgeBaseQueries:

    @pytest.mark.asyncio
    async def test_search_by_embedding(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[
            {"id": "kb-1", "title": "Password Reset", "similarity": 0.92}
        ])
        from production.database.queries.knowledge_base import search_by_embedding
        result = await search_by_embedding(pool, [0.1] * 1536)
        assert len(result) == 1
        assert result[0]["title"] == "Password Reset"

    @pytest.mark.asyncio
    async def test_insert_entry(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "kb-1", "title": "New Entry"})
        from production.database.queries.knowledge_base import insert_entry
        result = await insert_entry(pool, "New Entry", "Some content", "faq")
        assert result["title"] == "New Entry"

    @pytest.mark.asyncio
    async def test_get_by_category(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[{"category": "faq"}, {"category": "faq"}])
        from production.database.queries.knowledge_base import get_by_category
        result = await get_by_category(pool, "faq")
        assert len(result) == 2
