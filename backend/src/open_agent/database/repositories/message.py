from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.message import Message


class MessageRepository(Repository[Message]):
    model = Message

    async def list_by_run(self, user_id: str, run_id: UUID) -> list[Message]:
        return list(
            (
                await self.session.scalars(
                    select(Message)
                    .where(Message.user_id == user_id, Message.run_id == run_id)
                    .order_by(Message.sequence)
                )
            ).all()
        )
