"""Tests for LangGraph baseline execution and AgentRuntime execution boundary."""

import asyncio
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from open_agent.agents.base import Agent
from open_agent.agents.graph import build_messages_for_llm, create_agent_graph
from open_agent.agents.runtime import AgentRuntime
from open_agent.agents.state import AgentState
from open_agent.core.exceptions import AgentError
from open_agent.llm.base import LLMProvider


class MockLLMProvider:
    """Deterministic mock LLM provider for tests without external network calls."""

    def __init__(self, response_text: str = "Mock LLM answer", delay: float = 0.0) -> None:
        self.response_text = response_text
        self.delay = delay
        self.invoked_messages: list[list[BaseMessage]] = []

    async def generate(self, messages: list[BaseMessage]) -> AIMessage:
        self.invoked_messages.append(messages)
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        return AIMessage(content=self.response_text)


class FailingLLMProvider:
    """Mock LLM provider that intentionally raises an error."""

    def __init__(self, error_message: str = "Simulated API outage") -> None:
        self.error_message = error_message

    async def generate(self, messages: list[BaseMessage]) -> AIMessage:
        raise RuntimeError(self.error_message)


def test_build_messages_for_llm_with_prompt_only():
    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Tell me about quantum computing",
    )
    messages_to_send, active_history = build_messages_for_llm(
        state, system_prompt="You are a physics expert."
    )

    assert len(messages_to_send) == 2
    assert isinstance(messages_to_send[0], SystemMessage)
    assert messages_to_send[0].content == "You are a physics expert."
    assert isinstance(messages_to_send[1], HumanMessage)
    assert messages_to_send[1].content == "Tell me about quantum computing"

    assert len(active_history) == 1
    assert isinstance(active_history[0], HumanMessage)


def test_build_messages_for_llm_preserves_existing_history():
    existing = [
        SystemMessage(content="Existing system message"),
        HumanMessage(content="Previous question"),
        AIMessage(content="Previous answer"),
    ]
    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Follow up question",
        messages=existing,
    )
    messages_to_send, active_history = build_messages_for_llm(
        state, system_prompt="Alternative system prompt"
    )

    # Since existing history already had a SystemMessage, it shouldn't inject another one
    assert len(messages_to_send) == 3
    assert messages_to_send[0].content == "Existing system message"
    assert active_history == existing


@pytest.mark.asyncio
async def test_create_agent_graph_successful_execution():
    mock_llm = MockLLMProvider(response_text="Quantum computing uses qubits.")
    graph = create_agent_graph(llm=mock_llm, system_prompt="You are a helpful assistant.")

    initial_state = AgentState(
        user_id="user-123",
        agent_id="agent-abc",
        task_id="task-456",
        run_id="run-789",
        prompt="What is quantum computing?",
    )

    result = await graph.ainvoke(initial_state)
    state = AgentState(**result)

    assert state.status == "completed"
    assert state.current_step == 1
    assert state.error is None
    assert len(state.messages) == 2
    assert isinstance(state.messages[0], HumanMessage)
    assert state.messages[0].content == "What is quantum computing?"
    assert isinstance(state.messages[1], AIMessage)
    assert state.messages[1].content == "Quantum computing uses qubits."


@pytest.mark.asyncio
async def test_create_agent_graph_llm_failure_transitions_to_failed():
    failing_llm = FailingLLMProvider(error_message="Rate limit exceeded on provider")
    graph = create_agent_graph(llm=failing_llm)

    initial_state = AgentState(
        user_id="user-123",
        agent_id="agent-abc",
        task_id="task-456",
        run_id="run-789",
        prompt="Hello",
    )

    result = await graph.ainvoke(initial_state)
    state = AgentState(**result)

    assert state.status == "failed"
    assert state.current_step == 1
    assert "Rate limit exceeded on provider" in (state.error or "")
    assert len(state.messages) == 1
    assert isinstance(state.messages[0], HumanMessage)


@pytest.mark.asyncio
async def test_agent_runtime_execute_run_success():
    mock_llm = MockLLMProvider(response_text="Task completed successfully.")
    agent = Agent(
        agent_id="agent-1",
        name="Research Assistant",
        role="Researcher",
        llm=mock_llm,
        tools=[],
        description="Specializes in research summaries",
    )

    runtime = AgentRuntime(agent=agent, timeout_seconds=10.0, max_steps=5)
    initial_state = AgentState(
        user_id="user-1",
        agent_id=agent.agent_id,
        task_id="task-1",
        run_id="run-1",
        prompt="Summarize findings",
    )

    final_state = await runtime.execute_run(initial_state)

    assert final_state.status == "completed"
    assert final_state.current_step == 1
    assert final_state.error is None
    assert final_state.messages[-1].content == "Task completed successfully."


@pytest.mark.asyncio
async def test_agent_runtime_enforces_timeout():
    slow_llm = MockLLMProvider(response_text="Too late", delay=0.3)
    agent = Agent(
        agent_id="agent-1",
        name="Slow Agent",
        role="Worker",
        llm=slow_llm,
        tools=[],
    )

    runtime = AgentRuntime(agent=agent, timeout_seconds=0.05)
    initial_state = AgentState(
        user_id="user-1",
        agent_id=agent.agent_id,
        task_id="task-1",
        run_id="run-1",
        prompt="Quick question",
    )

    final_state = await runtime.execute_run(initial_state)

    assert final_state.status == "failed"
    assert "timed out" in (final_state.error or "").lower()


@pytest.mark.asyncio
async def test_agent_runtime_enforces_max_steps():
    mock_llm = MockLLMProvider()
    agent = Agent(
        agent_id="agent-1",
        name="Worker",
        role="Worker",
        llm=mock_llm,
        tools=[],
    )

    runtime = AgentRuntime(agent=agent, max_steps=3)
    initial_state = AgentState(
        user_id="user-1",
        agent_id=agent.agent_id,
        task_id="task-1",
        run_id="run-1",
        prompt="Looping task",
        current_step=3,
    )

    final_state = await runtime.execute_run(initial_state)

    assert final_state.status == "failed"
    assert "Maximum execution steps (3) exceeded" in (final_state.error or "")


@pytest.mark.asyncio
async def test_agent_runtime_validates_required_ids():
    mock_llm = MockLLMProvider()
    agent = Agent(
        agent_id="agent-1",
        name="Worker",
        role="Worker",
        llm=mock_llm,
        tools=[],
    )
    runtime = AgentRuntime(agent=agent)

    # Missing user_id
    invalid_state = AgentState(
        user_id="",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Hello",
    )
    with pytest.raises(AgentError, match="user_id"):
        await runtime.execute_run(invalid_state)

    # Missing agent_id
    invalid_state2 = AgentState(
        user_id="user-1",
        agent_id="",
        task_id="task-1",
        run_id="run-1",
        prompt="Hello",
    )
    with pytest.raises(AgentError, match="agent_id"):
        await runtime.execute_run(invalid_state2)


def test_agent_runtime_requires_agent_and_llm():
    with pytest.raises(AgentError, match="Agent must be provided"):
        AgentRuntime(agent=None)  # type: ignore[arg-type]

    agent_no_llm = Agent(
        agent_id="agent-1",
        name="Incomplete Agent",
        role="Worker",
        llm=None,  # type: ignore[arg-type]
        tools=[],
    )
    with pytest.raises(AgentError, match="must have an LLMProvider configured"):
        AgentRuntime(agent=agent_no_llm)
