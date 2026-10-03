"""Integration tests verifying AgentRuntime run, message, and tool call persistence."""

from uuid import uuid4
import pytest

pytest_asyncio = pytest.importorskip("pytest_asyncio")
pytest.importorskip("aiosqlite")
from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from open_agent.agents.base import Agent
from open_agent.agents.runtime import AgentRuntime
from open_agent.agents.state import AgentState
from open_agent.database.base import Base
from open_agent.database.enums import MessageRole, RunStatus, ToolCallStatus
from open_agent.database.repositories import (
    AgentRepository,
    AgentRunRepository,
    MessageRepository,
    TaskRepository,
    ToolCallRepository,
)
from open_agent.tools.base import Tool
from open_agent.tools.builtin import EchoTool


@pytest_asyncio.fixture
async def db_session():
    """Create an isolated, schema-initialized in-memory SQLite database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session

    await engine.dispose()


class SequenceMockLLM:
    """Mock LLM returning sequential predetermined AIMessages."""

    def __init__(self, responses: list[AIMessage]) -> None:
        self.responses = list(responses)
        self.idx = 0

    async def generate(
        self,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
    ) -> AIMessage:
        if self.idx < len(self.responses):
            resp = self.responses[self.idx]
            self.idx += 1
            return resp
        return AIMessage(content="Final default response")


@pytest.mark.asyncio
async def test_runtime_persists_successful_run_and_messages(db_session):
    user_id = "user-persisted-1"
    agent_id = str(uuid4())
    task_id = str(uuid4())
    run_id = str(uuid4())

    mock_llm = SequenceMockLLM([AIMessage(content="Persistent response")])
    agent = Agent(
        agent_id=agent_id,
        name="Persistence Worker",
        role="Worker",
        llm=mock_llm,
        tools=[],
    )

    runtime = AgentRuntime(agent=agent, session=db_session)
    state = AgentState(
        user_id=user_id,
        agent_id=agent_id,
        task_id=task_id,
        run_id=run_id,
        prompt="Initial prompt",
    )

    final_state = await runtime.execute_run(state)
    assert final_state.status == "completed"

    # Verify run record
    run_repo = AgentRunRepository(db_session)
    runs = await run_repo.list_by_user(user_id)
    assert len(runs) == 1
    assert runs[0].status == RunStatus.COMPLETED
    assert runs[0].current_step == 1
    assert runs[0].started_at is not None
    assert runs[0].completed_at is not None
    assert runs[0].error is None

    # Verify message records
    message_repo = MessageRepository(db_session)
    messages = await message_repo.list_by_run(user_id, runs[0].id)
    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "Initial prompt"
    assert messages[0].sequence == 0
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == "Persistent response"
    assert messages[1].sequence == 1


@pytest.mark.asyncio
async def test_runtime_persists_tool_calls_and_observations(db_session):
    user_id = "user-persisted-2"
    agent_id = str(uuid4())
    task_id = str(uuid4())
    run_id = str(uuid4())

    tool_call_resp = AIMessage(
        content="Echoing input.",
        tool_calls=[
            {
                "id": str(uuid4()),
                "name": "echo",
                "args": {"message": "persisted-echo"},
            }
        ],
    )
    final_resp = AIMessage(content="Echo completed successfully.")

    mock_llm = SequenceMockLLM([tool_call_resp, final_resp])
    agent = Agent(
        agent_id=agent_id,
        name="Tool Persistence Worker",
        role="Worker",
        llm=mock_llm,
        tools=[EchoTool()],
    )

    runtime = AgentRuntime(agent=agent)
    state = AgentState(
        user_id=user_id,
        agent_id=agent_id,
        task_id=task_id,
        run_id=run_id,
        prompt="Echo test",
    )

    final_state = await runtime.execute_run(state, session=db_session)
    assert final_state.status == "completed"

    # Verify tool calls in database
    tool_call_repo = ToolCallRepository(db_session)
    run_repo = AgentRunRepository(db_session)
    run = (await run_repo.list_by_user(user_id))[0]

    tool_calls = await tool_call_repo.list_by_run(user_id, run.id)
    assert len(tool_calls) == 1
    assert tool_calls[0].tool_name == "echo"
    assert tool_calls[0].status == ToolCallStatus.COMPLETED
    assert tool_calls[0].arguments == {"message": "persisted-echo"}
    assert tool_calls[0].result == {"output": "persisted-echo"}


@pytest.mark.asyncio
async def test_runtime_persists_failure_status(db_session):
    user_id = "user-persisted-3"
    agent_id = str(uuid4())
    task_id = str(uuid4())
    run_id = str(uuid4())

    class FailingLLM:
        async def generate(self, messages, tools=None):
            raise RuntimeError("Database outage simulated")

    agent = Agent(
        agent_id=agent_id,
        name="Failing Worker",
        role="Worker",
        llm=FailingLLM(),
        tools=[],
    )

    runtime = AgentRuntime(agent=agent, session=db_session)
    state = AgentState(
        user_id=user_id,
        agent_id=agent_id,
        task_id=task_id,
        run_id=run_id,
        prompt="Fail please",
    )

    final_state = await runtime.execute_run(state)
    assert final_state.status == "failed"

    run_repo = AgentRunRepository(db_session)
    runs = await run_repo.list_by_user(user_id)
    assert len(runs) == 1
    assert runs[0].status == RunStatus.FAILED
    assert "Database outage simulated" in (runs[0].error or "")
