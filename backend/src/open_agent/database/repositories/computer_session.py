from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.computer_session import ComputerSession
from open_agent.database.enums import ComputerSessionStatus


class ComputerSessionRepository(Repository[ComputerSession]):
    model = ComputerSession

    async def list_by_agent(
        self, user_id: str, agent_id: UUID
    ) -> list[ComputerSession]:
        return list(
            (
                await self.session.scalars(
                    select(ComputerSession)
                    .where(
                        ComputerSession.user_id == user_id,
                        ComputerSession.agent_id == agent_id,
                    )
                    .order_by(ComputerSession.created_at)
                )
            ).all()
        )

    async def update_status(
        self, user_id: str, item_id: UUID, status: ComputerSessionStatus, **values: Any
    ) -> ComputerSession | None:
        return await self.update(user_id, item_id, status=status, **values)
