from typing import Any
from uuid import UUID
from sqlalchemy import select
from open_agent.database.repositories.base import Repository
from open_agent.database.models.artifact import Artifact


class ArtifactRepository(Repository[Artifact]):
    model = Artifact

    async def list_by_run(self, user_id: str, run_id: UUID) -> list[Artifact]:
        return list(
            (
                await self.session.scalars(
                    select(Artifact)
                    .where(Artifact.user_id == user_id, Artifact.run_id == run_id)
                    .order_by(Artifact.created_at)
                )
            ).all()
        )
