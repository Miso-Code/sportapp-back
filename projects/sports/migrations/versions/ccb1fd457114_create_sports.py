"""Create Sports

Revision ID: ccb1fd457114
Revises:
Create Date: 2024-04-13 15:34:07.247218

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ccb1fd457114"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """
        CREATE TABLE IF NOT EXISTS sports (
            sport_id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
    """,
        ),
    )

    op.execute(
        sa.DDL(
            """
        INSERT INTO sports (sport_id, name)
        VALUES
            ('ee5a3a48-5b5a-48ca-94df-67556c99afdf', 'Cycling'),
            ('d459b8e8-3563-4d26-9ae3-d607696123d8', 'Athletics')
    """,
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.DDL(
            """
        DROP TABLE IF EXISTS sports CASCADE;
    """,
        ),
    )
