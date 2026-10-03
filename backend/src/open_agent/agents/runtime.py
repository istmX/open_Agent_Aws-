"""Execution boundary for a single agent."""

import asyncio
import logging
from typing import Any

from langgraph.graph.state import CompiledStateGraph

from open_agent.agents.base import Agent
from open_agent.agents.graph import create_agent_graph
from open_agent.agents.persistence import RunPersistenceService
from open_agent.agents.state import AgentState
from open_agent.core.exceptions import (
    AgentError,
    AgentStepLimitExceededError,
    AgentTimeoutError,
)

if False:  # TYPE_CHECKING
    from sqlalchemy.ext.asyncio import AsyncSession
else:
    AsyncSession = Any

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Execution boundary managing run execution, step limits, timeouts, and persistence."""

    def __init__(
        self,
        agent: Agent,
        *,
        max_steps: int = 10,
        timeout_seconds: float = 60.0,
        graph: CompiledStateGraph | None = None,
        session: Any | None = None,
    ) -> None:
        """Initialize the runtime for ``agent``."""
        if not agent:
            raise AgentError("Agent must be provided to AgentRuntime.")
        if agent.llm is None and graph is None:
            raise AgentError(
                f"Agent '{agent.name}' must have an LLMProvider configured."
            )

        self.agent = agent
        self.max_steps = max_steps
        self.timeout_seconds = timeout_seconds
        self.session = session

        system_prompt = f"You are {agent.name}, an AI assistant. Role: {agent.role}."
        if agent.description:
            system_prompt += f" Description: {agent.description}."

        self.graph: CompiledStateGraph = graph or create_agent_graph(
            llm=agent.llm,
            tools=agent.tools,
            system_prompt=system_prompt,
            max_steps=max_steps,
        )

    async def execute_run(
        self,
        state: AgentState,
        session: Any | None = None,
    ) -> AgentState:
        """Execute a single run within configured step and timeout boundaries, optionally persisting records."""
        if not state.user_id:
            raise AgentError("AgentState must include a valid user_id.")
        if not state.agent_id:
            raise AgentError("AgentState must include a valid agent_id.")

        active_session = session or self.session
        persistence = (
            RunPersistenceService(active_session) if active_session else None
        )

        if state.current_step >= self.max_steps:
            state.status = "failed"
            state.error = (
                f"Maximum execution steps ({self.max_steps}) exceeded."
            )
            logger.warning(
                "Run %s for agent %s aborted: max steps exceeded (%s >= %s)",
                state.run_id,
                self.agent.agent_id,
                state.current_step,
                self.max_steps,
            )
            if persistence:
                await persistence.complete_run(state)
            return state

        state.status = "running"
        if persistence:
            try:
                await persistence.start_run(state)
            except Exception as exc:
                logger.error(
                    "Failed to record run start for %s: %s",
                    state.run_id,
                    exc,
                    exc_info=True,
                )

        try:
            raw_result: dict[str, Any] = await asyncio.wait_for(
                self.graph.ainvoke(state),
                timeout=self.timeout_seconds,
            )
            final_state = AgentState(**raw_result)
        except TimeoutError:
            logger.error(
                "Run %s timed out after %s seconds",
                state.run_id,
                self.timeout_seconds,
            )
            state.status = "failed"
            state.error = f"Execution timed out after {self.timeout_seconds} seconds."
            final_state = state
        except Exception as exc:
            logger.error(
                "Run %s execution failed with error: %s",
                state.run_id,
                exc,
                exc_info=True,
            )
            state.status = "failed"
            state.error = str(exc)
            final_state = state

        if persistence:
            try:
                await persistence.complete_run(final_state)
            except Exception as exc:
                logger.error(
                    "Failed to record run completion for %s: %s",
                    state.run_id,
                    exc,
                    exc_info=True,
                )

        return final_state

