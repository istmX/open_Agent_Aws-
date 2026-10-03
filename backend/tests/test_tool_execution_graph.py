"""Tests for the LangGraph tool execution loop and runtime integration."""

from typing import Any
import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from pydantic import BaseModel, Field

from open_agent.agents.base import Agent
from open_agent.agents.graph import create_agent_graph
from open_agent.agents.runtime import AgentRuntime
from open_agent.agents.state import AgentState
from open_agent.core.exceptions import ToolError
from open_agent.tools.base import Tool
from open_agent.tools.builtin import EchoTool
from open_agent.tools.registry import ToolRegistry


class MockCalcInput(BaseModel):
    operation: str = Field(description="Operation: add, multiply, or divide")
    a: float
    b: float


class MockCalculatorTool(Tool):
    """Local test tool for arithmetic graph tests."""

    def __init__(self) -> None:
        super().__init__(name="calculator", description="Test calculator", args_schema=MockCalcInput)

    async def execute(self, operation: str, a: float, b: float, **kwargs: Any) -> float:
        if operation == "add":
            return a + b
        if operation == "multiply":
            return a * b
        if operation == "divide":
            if b == 0:
                raise ToolError("Division by zero is not allowed.")
            return a / b
        raise ToolError(f"Unsupported operation {operation}")



class SequenceMockLLM:
    """Mock LLM that yields responses from a predefined sequence."""

    def __init__(self, responses: list[AIMessage]) -> None:
        self.responses = list(responses)
        self.call_count = 0
        self.received_messages: list[list[BaseMessage]] = []

    async def generate(
        self,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
    ) -> AIMessage:
        self.received_messages.append(messages)
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return AIMessage(content="Default final response")


@pytest.mark.asyncio
async def test_tool_loop_single_tool_execution():
    tool_call_response = AIMessage(
        content="I will compute the sum.",
        tool_calls=[{"id": "call_123", "name": "calculator", "args": {"operation": "add", "a": 12.0, "b": 8.0}}],
    )
    final_response = AIMessage(content="The sum is 20.0.")

    mock_llm = SequenceMockLLM([tool_call_response, final_response])
    calc_tool = MockCalculatorTool()
    graph = create_agent_graph(llm=mock_llm, tools=[calc_tool])

    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="What is 12 + 8?",
    )

    result = await graph.ainvoke(state)
    final_state = AgentState(**result)

    assert final_state.status == "completed"
    assert final_state.current_step == 2
    assert final_state.error is None
    assert len(final_state.messages) == 4

    assert isinstance(final_state.messages[0], HumanMessage)
    assert isinstance(final_state.messages[1], AIMessage)
    assert isinstance(final_state.messages[2], ToolMessage)
    assert final_state.messages[2].content == "20.0"
    assert final_state.messages[2].tool_call_id == "call_123"
    assert isinstance(final_state.messages[3], AIMessage)
    assert final_state.messages[3].content == "The sum is 20.0."


@pytest.mark.asyncio
async def test_tool_loop_multiple_parallel_tool_calls():
    tool_call_response = AIMessage(
        content="Computing both operations.",
        tool_calls=[
            {"id": "call_1", "name": "calculator", "args": {"operation": "add", "a": 10.0, "b": 5.0}},
            {"id": "call_2", "name": "echo", "args": {"message": "Operation started"}},
        ],
    )
    final_response = AIMessage(content="Both done: 15.0 and confirmed.")

    mock_llm = SequenceMockLLM([tool_call_response, final_response])
    graph = create_agent_graph(
        llm=mock_llm,
        tools=[MockCalculatorTool(), EchoTool()],
    )

    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Perform operations",
    )


    result = await graph.ainvoke(state)
    final_state = AgentState(**result)

    assert final_state.status == "completed"
    assert final_state.current_step == 2
    # Human + AIMessage(tool_calls) + 2 ToolMessages + AIMessage(final)
    assert len(final_state.messages) == 5
    assert isinstance(final_state.messages[2], ToolMessage)
    assert final_state.messages[2].content == "15.0"
    assert isinstance(final_state.messages[3], ToolMessage)
    assert final_state.messages[3].content == "Operation started"


@pytest.mark.asyncio
async def test_tool_loop_handles_unregistered_tool():
    tool_call_response = AIMessage(
        content="",
        tool_calls=[{"id": "call_unknown", "name": "missing_tool", "args": {"param": "val"}}],
    )
    final_response = AIMessage(content="I could not find the requested tool.")

    mock_llm = SequenceMockLLM([tool_call_response, final_response])
    graph = create_agent_graph(llm=mock_llm, tools=[])

    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Use missing tool",
    )

    result = await graph.ainvoke(state)
    final_state = AgentState(**result)

    assert final_state.status == "completed"
    tool_msg = final_state.messages[2]
    assert isinstance(tool_msg, ToolMessage)
    assert "Error: Tool 'missing_tool' is not registered" in tool_msg.content


@pytest.mark.asyncio
async def test_tool_loop_handles_tool_exception():
    tool_call_response = AIMessage(
        content="",
        tool_calls=[{"id": "call_div_zero", "name": "calculator", "args": {"operation": "divide", "a": 5.0, "b": 0.0}}],
    )
    final_response = AIMessage(content="Caught division by zero error.")

    mock_llm = SequenceMockLLM([tool_call_response, final_response])
    graph = create_agent_graph(llm=mock_llm, tools=[MockCalculatorTool()])

    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Divide 5 by 0",
    )

    result = await graph.ainvoke(state)
    final_state = AgentState(**result)

    assert final_state.status == "completed"
    tool_msg = final_state.messages[2]
    assert isinstance(tool_msg, ToolMessage)
    assert "Division by zero is not allowed" in tool_msg.content


@pytest.mark.asyncio
async def test_tool_loop_enforces_max_steps():
    infinite_tool_response = AIMessage(
        content="Calling tool again...",
        tool_calls=[{"id": "call_loop", "name": "echo", "args": {"message": "loop"}}],
    )
    mock_llm = SequenceMockLLM([infinite_tool_response] * 10)
    graph = create_agent_graph(
        llm=mock_llm,
        tools=[EchoTool()],
        max_steps=3,
    )

    state = AgentState(
        user_id="user-1",
        agent_id="agent-1",
        task_id="task-1",
        run_id="run-1",
        prompt="Loop forever",
    )

    result = await graph.ainvoke(state)
    final_state = AgentState(**result)

    assert final_state.status == "failed"
    assert "Maximum execution steps (3) exceeded" in (final_state.error or "")


@pytest.mark.asyncio
async def test_agent_runtime_with_tools_integration():
    tool_call_response = AIMessage(
        content="Computing result.",
        tool_calls=[{"id": "call_runtime", "name": "calculator", "args": {"operation": "multiply", "a": 6.0, "b": 7.0}}],
    )
    final_response = AIMessage(content="6 times 7 is 42.0.")

    mock_llm = SequenceMockLLM([tool_call_response, final_response])
    agent = Agent(
        agent_id="calc-agent-1",
        name="Calculator Bot",
        role="Math Assistant",
        llm=mock_llm,
        tools=[MockCalculatorTool()],
    )

    runtime = AgentRuntime(agent=agent, max_steps=5)
    initial_state = AgentState(
        user_id="user-1",
        agent_id=agent.agent_id,
        task_id="task-1",
        run_id="run-1",
        prompt="Multiply 6 by 7",
    )

    final_state = await runtime.execute_run(initial_state)

    assert final_state.status == "completed"
    assert final_state.current_step == 2
    assert final_state.messages[-1].content == "6 times 7 is 42.0."

