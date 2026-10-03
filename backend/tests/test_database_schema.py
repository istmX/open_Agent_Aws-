from sqlalchemy.orm import configure_mappers
from open_agent.database.base import Base
from open_agent.database.url import async_database_url
import open_agent.database.models  # noqa: F401


def test_ai_schema_has_all_owner_scoped_tables_and_no_user_table():
    configure_mappers()
    assert set(Base.metadata.tables) == {
        "agents",
        "tasks",
        "agent_runs",
        "messages",
        "tool_calls",
        "computer_sessions",
        "artifacts",
    }
    assert "users" not in Base.metadata.tables
    for table in Base.metadata.tables.values():
        assert "user_id" in table.c
        assert not table.c.user_id.nullable


def test_relationship_foreign_keys_and_ownership_indexes_exist():
    required_fks = {
        "tasks": {"agent_id": "agents"},
        "agent_runs": {"task_id": "tasks", "agent_id": "agents"},
        "messages": {"run_id": "agent_runs"},
        "tool_calls": {"run_id": "agent_runs", "agent_id": "agents"},
        "computer_sessions": {"agent_id": "agents"},
        "artifacts": {"run_id": "agent_runs", "agent_id": "agents"},
    }
    for table_name, columns in required_fks.items():
        table = Base.metadata.tables[table_name]
        for column, target in columns.items():
            assert (
                next(iter(table.c[column].foreign_keys)).target_fullname
                == f"{target}.id"
            )
            assert next(iter(table.c[column].foreign_keys)).ondelete == "RESTRICT"
    for table in Base.metadata.tables.values():
        assert any(
            index
            for index in table.indexes
            if "user_id" in {column.name for column in index.columns}
        )
    assert "updated_at" in Base.metadata.tables["computer_sessions"].c


def test_database_url_normalizes_neon_ssl_options_for_asyncpg():
    normalized = async_database_url(
        "postgresql://user:pass@example.test/db?sslmode=require&channel_binding=require"
    )
    assert normalized.startswith("postgresql+asyncpg://")
    assert "ssl=require" in normalized
    assert "sslmode" not in normalized
    assert "channel_binding" not in normalized
