"""LangGraph orchestration graph for agent execution with tool loop."""

import logging
import uuid
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from open_agent.agents.state import AgentState
from open_agent.llm.base import LLMProvider
from open_agent.tools.base import Tool
from open_agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def build_messages_for_llm(
    state: AgentState,
    system_prompt: str | None = None,
) -> tuple[list[BaseMessage], list[BaseMessage]]:
    """Prepare messages to send to the LLM and the active conversation history.

    Returns:
        tuple[list[BaseMessage], list[BaseMessage]]:
            1. The messages list to send to the LLM (including SystemMessage if configured)
            2. The active messages list to record in state history
    """
    has_system_message = any(isinstance(m, SystemMessage) for m in state.messages)
    active_history = list(state.messages)

    if not active_history and state.prompt:
        active_history.append(HumanMessage(content=state.prompt))

    messages_to_send: list[BaseMessage] = []
    if system_prompt and not has_system_message:
        messages_to_send.append(SystemMessage(content=system_prompt))
    messages_to_send.extend(active_history)

    return messages_to_send, active_history


def create_agent_graph(
    llm: LLMProvider,
    tools: list[Tool] | ToolRegistry | None = None,
    system_prompt: str | None = None,
    max_steps: int = 10,
) -> CompiledStateGraph:
    """Build and compile the LangGraph workflow: START -> call_llm <-> execute_tools -> END."""
    if isinstance(tools, ToolRegistry):
        tool_registry = tools
    else:
        tool_registry = ToolRegistry(tools or [])

    registered_tools = tool_registry.list_tools()

    async def call_llm(state: AgentState) -> dict[str, Any]:
        """Invoke LLM provider, update steps, and transition execution status."""
        if state.current_step >= max_steps:
            return {
                "status": "failed",
                "error": f"Maximum execution steps ({max_steps}) exceeded.",
            }

        messages_to_send, active_history = build_messages_for_llm(
            state, system_prompt=system_prompt
        )

        try:
            tools_to_pass = registered_tools if registered_tools else None
            try:
                response: AIMessage = await llm.generate(
                    messages_to_send, tools=tools_to_pass
                )
            except TypeError:
                response = await llm.generate(messages_to_send)

            has_tool_calls = bool(getattr(response, "tool_calls", None))
            new_step = state.current_step + 1

            if not has_tool_calls:
                return {
                    "messages": active_history + [response],
                    "current_step": new_step,
                    "status": "completed",
                    "error": None,
                }

            if new_step >= max_steps:
                return {
                    "messages": active_history + [response],
                    "current_step": new_step,
                    "status": "failed",
                    "error": f"Maximum execution steps ({max_steps}) exceeded.",
                }

            return {
                "messages": active_history + [response],
                "current_step": new_step,
                "status": "running",
                "error": None,
            }
        except Exception as exc:
            logger.error("LLM node execution failed: %s", exc, exc_info=True)
            return {
                "messages": active_history,
                "current_step": state.current_step + 1,
                "status": "failed",
                "error": str(exc),
            }

    async def execute_tools(state: AgentState) -> dict[str, Any]:
        """Execute tool calls from the latest AIMessage and record observations."""
        last_message = state.messages[-1] if state.messages else None
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {}

        tool_messages: list[ToolMessage] = []
        for call in last_message.tool_calls:
            call_id = call.get("id") or str(uuid.uuid4())
            tool_name = call.get("name", "")
            raw_args = call.get("args") or {}
            tool_args = raw_args if isinstance(raw_args, dict) else {}

            tool = tool_registry.get_optional(tool_name)
            if tool is None:
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: Tool '{tool_name}' is not registered.",
                        tool_call_id=call_id,
                        name=tool_name,
                    )
                )
                continue

            try:
                result = await tool.execute(**tool_args)
                content = str(result) if not isinstance(result, str) else result
                tool_messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=call_id,
                        name=tool_name,
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Tool '%s' execution raised an exception: %s",
                    tool_name,
                    exc,
                    exc_info=True,
                )
                tool_messages.append(
                    ToolMessage(
                        content=f"Error executing tool '{tool_name}': {exc}",
                        tool_call_id=call_id,
                        name=tool_name,
                    )
                )

        return {
            "messages": list(state.messages) + tool_messages,
        }

    def route_after_llm(state: AgentState) -> str:
        """Route to tool execution or terminate the workflow."""
        if state.status == "failed" or state.status == "completed":
            return END

        last_message = state.messages[-1] if state.messages else None
        if (
            isinstance(last_message, AIMessage)
            and getattr(last_message, "tool_calls", None)
            and state.current_step < max_steps
        ):
            return "execute_tools"

        return END

    builder = StateGraph(AgentState)
    builder.add_node("call_llm", call_llm)
    builder.add_node("execute_tools", execute_tools)

    builder.add_edge(START, "call_llm")
    builder.add_conditional_edges(
        "call_llm",
        route_after_llm,
        {
            "execute_tools": "execute_tools",
            END: END,
        },
    )
    builder.add_edge("execute_tools", "call_llm")

    return builder.compile()

