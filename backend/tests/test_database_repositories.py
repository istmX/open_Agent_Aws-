from uuid import uuid4

import pytest

pytest_asyncio = pytest.importorskip("pytest_asyncio")
pytest.importorskip("aiosqlite")
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from open_agent.database.base import Base
from open_agent.database.enums import (
    AgentStatus,
    MessageRole,
    RunStatus,
    TaskStatus,
    ToolCallStatus,
)
from open_agent.database.models import (
    Agent,
    AgentRun,
    Artifact,
    ComputerSession,
    Message,
    Task,
    ToolCall,
)
from open_agent.database.repositories import (
    AgentRepository,
    AgentRunRepository,
    ArtifactRepository,
    ComputerSessionRepository,
    MessageRepository,
    TaskRepository,
    ToolCallRepository,
)


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
        await db.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_agent_create_count_and_user_isolation(session):
    repo = AgentRepository(session)
    first = await repo.create(
        user_id="user-a",
        name="one",
        role="assistant",
        configuration={"provider": "groq"},
    )
    second = await repo.create(user_id="user-a", name="two", role="assistant")
    await repo.create(user_id="user-b", name="one", role="assistant")
    assert await repo.count_by_user("user-a") == 2
    assert len(await repo.list_by_user("user-a")) == 2
    assert await repo.count_by_user("user-b") == 1
    assert await repo.get_by_id("user-b", second.id) is None
    assert first.created_at is not None and first.updated_at is not None
    assert first.configuration == {"provider": "groq"}


@pytest.mark.asyncio
async def test_agent_name_uniqueness_is_scoped_to_user(session):
    repo = AgentRepository(session)
    await repo.create(user_id="user-a", name="worker", role="assistant")
    await repo.create(user_id="user-b", name="worker", role="assistant")
    with pytest.raises(IntegrityError):
        async with session.begin_nested():
            await repo.create(user_id="user-a", name="worker", role="assistant")


@pytest.mark.asyncio
async def test_resource_lifecycle_and_status_updates(session):
    agent = await AgentRepository(session).create(
        user_id="user-a", name="worker", role="assistant"
    )
    task = await TaskRepository(session).create(
        agent_id=agent.id, user_id="user-a", prompt="do work"
    )
    run = await AgentRunRepository(session).create(
        task_id=task.id, agent_id=agent.id, user_id="user-a"
    )
    messages = MessageRepository(session)
    await messages.create(
        run_id=run.id,
        user_id="user-a",
        role=MessageRole.USER,
        content="hello",
        sequence=1,
    )
    await messages.create(
        run_id=run.id,
        user_id="user-a",
        role=MessageRole.ASSISTANT,
        content="done",
        sequence=2,
    )
    assert [m.sequence for m in await messages.list_by_run("user-a", run.id)] == [1, 2]
    calls = ToolCallRepository(session)
    call = await calls.create(
        run_id=run.id,
        agent_id=agent.id,
        user_id="user-a",
        tool_name="search",
        arguments={"q": "x"},
    )
    await calls.update(
        "user-a", call.id, status=ToolCallStatus.COMPLETED, result={"ok": True}
    )
    assert (await calls.get_by_id("user-a", call.id)).status == ToolCallStatus.COMPLETED
    computer = await ComputerSessionRepository(session).create(
        agent_id=agent.id, user_id="user-a", provider="local"
    )
    assert computer.agent_id == agent.id
    artifact = await ArtifactRepository(session).create(
        run_id=run.id,
        agent_id=agent.id,
        user_id="user-a",
        name="out",
        type="text",
        storage_key="pending/out",
    )
    assert artifact.storage_key == "pending/out"
    await TaskRepository(session).update_status("user-a", task.id, TaskStatus.RUNNING)
    await AgentRunRepository(session).update_status(
        "user-a", run.id, RunStatus.COMPLETED
    )
    assert (
        await TaskRepository(session).get_by_id("user-a", task.id)
    ).status == TaskStatus.RUNNING
    assert await ArtifactRepository(session).list_by_run("another-user", run.id) == []


@pytest.mark.asyncio
async def test_foreign_keys_and_agent_delete_preserves_audit_history(session):
    agent_repo = AgentRepository(session)
    with pytest.raises(IntegrityError):
        session.add(Task(agent_id=uuid4(), user_id="u", prompt="invalid"))
        await session.flush()
    await session.rollback()
    agent = await agent_repo.create(user_id="u", name="worker", role="assistant")
    task = await TaskRepository(session).create(
        agent_id=agent.id, user_id="u", prompt="x"
    )
    run = await AgentRunRepository(session).create(
        task_id=task.id, agent_id=agent.id, user_id="u"
    )
    await MessageRepository(session).create(
        run_id=run.id,
        user_id="u",
        role=MessageRole.SYSTEM,
        content="system",
        sequence=0,
    )
    await session.flush()
    with pytest.raises(IntegrityError):
        async with session.begin_nested():
            await agent_repo.delete("u", agent.id)
    assert await session.get(Task, task.id) is not None
    assert await session.get(AgentRun, run.id) is not None
    assert await session.scalar(__import__("sqlalchemy").select(Message)) is not None
