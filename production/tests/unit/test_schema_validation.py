"""Unit tests for schema DDL validation — T008 TDD target."""
import pathlib
import pytest

SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[2] / "database" / "schema.sql"

EXPECTED_TABLES = [
    "customers",
    "customer_identifiers",
    "conversations",
    "messages",
    "tickets",
    "knowledge_base",
    "channel_configs",
    "agent_metrics",
]


class TestSchemaValidation:
    """Validate schema.sql is syntactically present and complete."""

    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists(), "schema.sql not found"

    def test_schema_not_empty(self):
        content = SCHEMA_PATH.read_text(encoding="utf-8")
        assert len(content) > 1000, "schema.sql seems too short"

    @pytest.mark.parametrize("table_name", EXPECTED_TABLES)
    def test_table_present(self, table_name):
        content = SCHEMA_PATH.read_text(encoding="utf-8").lower()
        assert f"create table" in content and table_name in content, (
            f"Table {table_name} not found in schema.sql"
        )

    def test_pgvector_extension(self):
        content = SCHEMA_PATH.read_text(encoding="utf-8").lower()
        assert 'create extension' in content and 'vector' in content

    def test_ticket_number_trigger(self):
        content = SCHEMA_PATH.read_text(encoding="utf-8").lower()
        assert 'generate_ticket_number' in content

    def test_updated_at_trigger(self):
        content = SCHEMA_PATH.read_text(encoding="utf-8").lower()
        assert 'update_updated_at' in content
