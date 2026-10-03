from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.run import AgentRun
from open_agent.database.enums import RunStatus


class AgentRunRepository(Repository[AgentRun]):
    model = AgentRun

    async def list_by_task(self, user_id: str, task_id: UUID) -> list[AgentRun]:
        return list(
            (
                await self.session.scalars(
                    select(AgentRun)
                    .where(AgentRun.user_id == user_id, AgentRun.task_id == task_id)
                    .order_by(AgentRun.created_at)
                )
            ).all()
        )

    async def list_by_user(self, user_id: str) -> list[AgentRun]:
        return list(
            (
                await self.session.scalars(
                    select(AgentRun)
                    .where(AgentRun.user_id == user_id)
                    .order_by(AgentRun.created_at)
                )
            ).all()
        )

    async def update_status(
        self, user_id: str, run_id: UUID, status: RunStatus, **values: Any
    ) -> AgentRun | None:
        return await self.update(user_id, run_id, status=status, **values)
