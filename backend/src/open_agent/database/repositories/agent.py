from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.agent import Agent


class AgentRepository(Repository[Agent]):
    model = Agent

    async def list_by_user(self, user_id: str) -> list[Agent]:
        return list(
            (
                await self.session.scalars(
                    select(Agent)
                    .where(Agent.user_id == user_id)
                    .order_by(Agent.created_at)
                )
            ).all()
        )

    async def count_by_user(self, user_id: str) -> int:
        from sqlalchemy import func

        return int(
            await self.session.scalar(
                select(func.count()).select_from(Agent).where(Agent.user_id == user_id)
            )
            or 0
        )

    async def get_by_id(self, user_id: str, item_id: UUID) -> Agent | None:
        return await super().get_by_id(user_id, item_id)
