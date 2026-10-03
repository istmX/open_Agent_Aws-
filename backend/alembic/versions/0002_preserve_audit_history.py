"""Preserve execution history when parent resources are deleted.

Revision ID: 0002_preserve_audit_history
Revises: 0001_ai_persistence
"""

from alembic import op


revision = "0002_preserve_audit_history"
down_revision = "0001_ai_persistence"
branch_labels = None
depends_on = None


_FOREIGN_KEYS = (
    ("tasks", "fk_tasks_agent_id_agents", "agent_id", "agents"),
    ("agent_runs", "fk_agent_runs_task_id_tasks", "task_id", "tasks"),
    ("agent_runs", "fk_agent_runs_agent_id_agents", "agent_id", "agents"),
    ("messages", "fk_messages_run_id_agent_runs", "run_id", "agent_runs"),
    ("tool_calls", "fk_tool_calls_run_id_agent_runs", "run_id", "agent_runs"),
    ("tool_calls", "fk_tool_calls_agent_id_agents", "agent_id", "agents"),
    (
        "computer_sessions",
        "fk_computer_sessions_agent_id_agents",
        "agent_id",
        "agents",
    ),
    ("artifacts", "fk_artifacts_run_id_agent_runs", "run_id", "agent_runs"),
    ("artifacts", "fk_artifacts_agent_id_agents", "agent_id", "agents"),
)


def upgrade() -> None:
    for table, name, column, referred_table in _FOREIGN_KEYS:
        _set_delete_rule(table, name, column, referred_table, "RESTRICT", "r")
    op.execute(
        "ALTER TABLE computer_sessions ADD COLUMN IF NOT EXISTS "
        "updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE computer_sessions DROP COLUMN IF EXISTS updated_at")
    for table, name, column, referred_table in _FOREIGN_KEYS:
        _set_delete_rule(table, name, column, referred_table, "CASCADE", "c")


def _set_delete_rule(
    table: str,
    name: str,
    column: str,
    referred_table: str,
    rule: str,
    catalog_code: str,
) -> None:
    """Change only existing FKs whose delete rule does not already match."""
    op.execute(
        f"""DO $migration$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = '{name}'
              AND conrelid = '{table}'::regclass
              AND confdeltype <> '{catalog_code}'
          ) THEN
            ALTER TABLE {table} DROP CONSTRAINT {name};
            ALTER TABLE {table} ADD CONSTRAINT {name}
              FOREIGN KEY ({column}) REFERENCES {referred_table} (id)
              ON DELETE {rule};
          END IF;
        END
        $migration$"""
    )
