"""Create food limitations

Revision ID: 4eee161e3eef
Revises: 6d01b104ba29
Create Date: 2024-04-09 23:16:17.165341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4eee161e3eef"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """
        CREATE TABLE IF NOT EXISTS nutritional_limitations (
            limitation_id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL
        );
    """,
        ),
    )

    op.execute(
        sa.DDL(
            """
        INSERT INTO nutritional_limitations (limitation_id, name, description)
        VALUES
            ('af8bd914-753f-4c38-bce9-3643e365d1cc', 'lactose', 'No lactose'),
            ('e8ee04f9-4ef3-429f-84d9-289cc49f264b', 'seafood', 'No seafood'),
            ('a589bc34-796f-4490-ac04-342f9a3377eb', 'nuts', 'No nuts'),
            ('bf5e2e7f-9321-4bb1-a152-1319668f6fb3', 'sugar', 'No sugar'),
            ('8be124e1-5c2f-4027-b435-fdf51080a519', 'gluten', 'No gluten')
    """,
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.DDL(
            """
        DROP TABLE IF EXISTS nutritional_limitations CASCADE;
    """,
        ),
    )
