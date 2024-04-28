"""Create trainers

Revision ID: 2544812b6ab7
Revises: 4eee161e3eef
Create Date: 2024-04-26 23:16:23.471011

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2544812b6ab7"
down_revision: Union[str, None] = "4eee161e3eef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """
        CREATE TABLE IF NOT EXISTS trainers (
            trainer_id UUID PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL
        );
    """,
        ),
    )

    op.execute(
        sa.DDL(
            """
        INSERT INTO trainers (trainer_id, first_name, last_name)
        VALUES
            ('50a5a9fb-3ed3-4e6c-a2d6-39b148c0e6dc', 'John', 'Doe'),
            ('7e2de02d-09eb-438c-8cb1-0ed4e59ef28f', 'Jane', 'Smith'),
            ('3fe3f61b-05a8-4654-8e95-41f8456f4d02', 'Michael', 'Johnson'),
            ('1bf250ad-1911-494a-a3a4-dc92e68c89d9', 'Emily', 'Brown'),
            ('6c16d14e-9c88-4e4a-9b9e-0ef1bf413438', 'David', 'Lee');
    """,
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.DDL(
            """
        DROP TABLE IF EXISTS trainers CASCADE;
    """,
        ),
    )
