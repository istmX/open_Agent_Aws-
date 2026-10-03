from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.tool_call import ToolCall
from open_agent.database.enums import ToolCallStatus


class ToolCallRepository(Repository[ToolCall]):
    model = ToolCall

    async def list_by_run(self, user_id: str, run_id: UUID) -> list[ToolCall]:
        return list(
            (
                await self.session.scalars(
                    select(ToolCall)
                    .where(ToolCall.user_id == user_id, ToolCall.run_id == run_id)
                    .order_by(ToolCall.created_at)
                )
            ).all()
        )

    async def update_status(
        self, user_id: str, item_id: UUID, status: ToolCallStatus, **values: Any
    ) -> ToolCall | None:
        return await self.update(user_id, item_id, status=status, **values)
