from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.task import Task
from open_agent.database.enums import TaskStatus


class TaskRepository(Repository[Task]):
    model = Task

    async def list_by_agent(self, user_id: str, agent_id: UUID) -> list[Task]:
        return list(
            (
                await self.session.scalars(
                    select(Task)
                    .where(Task.user_id == user_id, Task.agent_id == agent_id)
                    .order_by(Task.created_at)
                )
            ).all()
        )

    async def list_by_user(self, user_id: str) -> list[Task]:
        return list(
            (
                await self.session.scalars(
                    select(Task)
                    .where(Task.user_id == user_id)
                    .order_by(Task.created_at)
                )
            ).all()
        )

    async def update_status(
        self, user_id: str, task_id: UUID, status: TaskStatus, **values: Any
    ) -> Task | None:
        return await self.update(user_id, task_id, status=status, **values)
