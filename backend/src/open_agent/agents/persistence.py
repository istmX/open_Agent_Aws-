"""Service bridging AgentRuntime execution lifecycle to repository persistence."""

import logging
from datetime import datetime, timezone
import uuid
from uuid import UUID

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from sqlalchemy.ext.asyncio import AsyncSession

from open_agent.agents.state import AgentState
from open_agent.database.enums import MessageRole, RunStatus, ToolCallStatus
from open_agent.database.repositories.agent import AgentRepository
from open_agent.database.repositories.message import MessageRepository
from open_agent.database.repositories.run import AgentRunRepository
from open_agent.database.repositories.task import TaskRepository
from open_agent.database.repositories.tool_call import ToolCallRepository

logger = logging.getLogger(__name__)


def parse_uuid(val: str) -> UUID:
    """Safely parse a string to a UUID, falling back to deterministic uuid5."""
    try:
        return UUID(val)
    except (ValueError, TypeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))


def map_message_role(msg: BaseMessage) -> MessageRole:
    """Map LangChain message instance to database MessageRole enum."""
    if isinstance(msg, HumanMessage):
        return MessageRole.USER
    if isinstance(msg, AIMessage):
        return MessageRole.ASSISTANT
    if isinstance(msg, ToolMessage):
        return MessageRole.TOOL
    if isinstance(msg, SystemMessage):
        return MessageRole.SYSTEM
    return MessageRole.USER


class RunPersistenceService:
    """Coordinates persistence of runs, messages, and tool calls across repositories."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.agent_repo = AgentRepository(session)
        self.task_repo = TaskRepository(session)
        self.run_repo = AgentRunRepository(session)
        self.message_repo = MessageRepository(session)
        self.tool_call_repo = ToolCallRepository(session)

    async def start_run(self, state: AgentState) -> UUID:
        """Create or update the run record when execution begins."""
        run_uuid = parse_uuid(state.run_id)
        task_uuid = parse_uuid(state.task_id)
        agent_uuid = parse_uuid(state.agent_id)
        now = datetime.now(timezone.utc)

        # Ensure parent entities exist to satisfy foreign key constraints
        agent = await self.agent_repo.get_by_id(state.user_id, agent_uuid)
        if not agent:
            await self.agent_repo.create(
                id=agent_uuid,
                user_id=state.user_id,
                name=f"agent-{state.agent_id}",
                role="assistant",
            )

        task = await self.task_repo.get_by_id(state.user_id, task_uuid)
        if not task:
            await self.task_repo.create(
                id=task_uuid,
                agent_id=agent_uuid,
                user_id=state.user_id,
                prompt=state.prompt or "Untitled task",
            )

        existing_run = await self.run_repo.get_by_id(state.user_id, run_uuid)
        if existing_run:
            await self.run_repo.update(
                state.user_id,
                run_uuid,
                status=RunStatus.RUNNING,
                started_at=now,
            )
        else:
            await self.run_repo.create(
                id=run_uuid,
                task_id=task_uuid,
                agent_id=agent_uuid,
                user_id=state.user_id,
                status=RunStatus.RUNNING,
                started_at=now,
                current_step=state.current_step,
            )

        await self.session.flush()
        return run_uuid

    async def complete_run(self, state: AgentState) -> None:
        """Persist final run status, conversation messages, and tool calls."""
        run_uuid = parse_uuid(state.run_id)
        agent_uuid = parse_uuid(state.agent_id)
        now = datetime.now(timezone.utc)

        run_status = (
            RunStatus.COMPLETED if state.status == "completed" else RunStatus.FAILED
        )

        await self.run_repo.update(
            state.user_id,
            run_uuid,
            status=run_status,
            completed_at=now,
            current_step=state.current_step,
            error=state.error,
        )

        # Persist conversation messages
        for seq, msg in enumerate(state.messages):
            role = map_message_role(msg)
            content = str(msg.content)
            await self.message_repo.create(
                run_id=run_uuid,
                user_id=state.user_id,
                role=role,
                content=content,
                sequence=seq,
            )

        # Index tool messages by tool_call_id for matching observations
        tool_results_by_id: dict[str, ToolMessage] = {
            m.tool_call_id: m
            for m in state.messages
            if isinstance(m, ToolMessage) and getattr(m, "tool_call_id", None)
        }

        # Persist tool calls made during execution
        for msg in state.messages:
            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                for call in msg.tool_calls:
                    call_id_str = call.get("id", "")
                    call_uuid = parse_uuid(call_id_str)
                    tool_name = call.get("name", "unknown")
                    raw_args = call.get("args") or {}
                    args_dict = (
                        raw_args if isinstance(raw_args, dict) else {"args": raw_args}
                    )

                    tool_msg = tool_results_by_id.get(call_id_str)
                    if tool_msg:
                        output_str = str(tool_msg.content)
                        is_error = output_str.startswith(
                            "Error:"
                        ) or output_str.startswith("Error executing")
                        status = (
                            ToolCallStatus.FAILED
                            if is_error
                            else ToolCallStatus.COMPLETED
                        )
                        result_dict = {"output": output_str}
                        error_text = output_str if is_error else None
                    else:
                        status = ToolCallStatus.FAILED
                        result_dict = None
                        error_text = "Tool call did not produce an observation"

                    await self.tool_call_repo.create(
                        id=call_uuid,
                        run_id=run_uuid,
                        agent_id=agent_uuid,
                        user_id=state.user_id,
                        tool_name=tool_name,
                        arguments=args_dict,
                        result=result_dict,
                        status=status,
                        error=error_text,
                        completed_at=now,
                    )

        await self.session.commit()
