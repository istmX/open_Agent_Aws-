# ERR.md — Error Log & Resolution History

This document records significant errors, root causes, fixes, affected subsystems, and regression prevention measures across the Open Agent AWS project.

---

## Incident 001: SQLite In-Memory Transaction Invalidation in Repository Test

- **Subsystem**: Database / Repository Tests (`backend/tests/test_database_repositories.py`)
- **Symptoms**: `AssertionError: assert None is not None` on line 167 of `test_database_repositories.py`.
- **Root Cause**: In `test_foreign_keys_and_agent_delete_preserves_audit_history`, `agent_repo.delete("u", agent.id)` raised an expected `IntegrityError` due to foreign key restrictions. However, because the test subsequently called `session.rollback()` without having committed the earlier record creation, the entire outer transaction was rolled back, clearing the previously created `Task` and `AgentRun`.
- **Fix**: Wrapped the deletion attempt in `async with session.begin_nested():` to create a scoped SQLite savepoint. The expected `IntegrityError` rolls back only the savepoint, leaving the outer transaction and flushed entities intact.
- **Regression Prevention**: Always use `session.begin_nested()` when asserting expected database integrity errors in unit tests with uncommitted fixtures.

---

## Incident 002: Positional Argument Mismatch in `test_agent.py`

- **Subsystem**: Agent Domain Model (`backend/src/open_agent/agents/test_agent.py`)
- **Symptoms**: `TypeError: Agent.__init__() missing 1 required positional argument: 'tools'` when executing `test_agent.py`.
- **Root Cause**: `Agent.__init__` was updated to accept `tools: list[Tool]`, but `test_agent.py` instantiated `Agent` without the `tools` parameter.
- **Fix**: Passed `tools=[]` to the `Agent` constructor and added assertion `assert agent.tools == []`.
- **Regression Prevention**: Standardize automated testing with `pytest` in `backend/tests/` rather than standalone test scripts, and ensure all constructor call sites update when domain models evolve.
