from typing import Any, Generic, TypeVar
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from open_agent.database.base import Base

Model = TypeVar("Model", bound=Base)


class Repository(Generic[Model]):
    model: type[Model]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **values: Any) -> Model:
        """Reject parent IDs that do not belong to the supplied external owner."""
        parent_for = {
            "Task": {"agent_id": "agents"},
            "AgentRun": {"task_id": "tasks", "agent_id": "agents"},
            "Message": {"run_id": "agent_runs"},
            "ToolCall": {"run_id": "agent_runs", "agent_id": "agents"},
            "ComputerSession": {"agent_id": "agents"},
            "Artifact": {"run_id": "agent_runs", "agent_id": "agents"},
        }
        owner = values.get("user_id")
        for field, table_name in parent_for.get(self.model.__name__, {}).items():
            parent = Base.metadata.tables[table_name]
            parent_id = values.get(field)
            if parent_id is None:
                continue
            query = select(parent.c.id).where(
                parent.c.id == parent_id, parent.c.user_id == owner
            )
            if table_name == "tasks" and self.model.__name__ == "AgentRun":
                query = query.where(parent.c.agent_id == values.get("agent_id"))
            if table_name == "agent_runs" and self.model.__name__ in {
                "ToolCall",
                "Artifact",
            }:
                query = query.where(parent.c.agent_id == values.get("agent_id"))
            if await self.session.scalar(query) is None:
                raise PermissionError(
                    f"{field} is missing or does not belong to user_id"
                )
        item = self.model(**values)
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, user_id: str, item_id: UUID) -> Model | None:
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == item_id, self.model.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, user_id: str, item_id: UUID) -> bool:
        item = await self.get_by_id(user_id, item_id)
        if item is None:
            return False
        await self.session.delete(item)
        await self.session.flush()
        return True

    async def update(self, user_id: str, item_id: UUID, **values: Any) -> Model | None:
        item = await self.get_by_id(user_id, item_id)
        if item is None:
            return None
        for key, value in values.items():
            if key not in {"id", "user_id", "agent_id", "task_id", "run_id"}:
                setattr(item, key, value)
        await self.session.flush()
        return item
