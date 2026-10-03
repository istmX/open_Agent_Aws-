"""Initial AI-side persistence schema."""

from alembic import op
import open_agent.database.models  # noqa: F401
from open_agent.database.base import Base

revision = "0001_ai_persistence"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
