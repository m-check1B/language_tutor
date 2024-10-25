"""add updated_at to conversation

Revision ID: 55e4d1503dfd
Revises: 
Create Date: 2024-10-25 13:44:08.218954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55e4d1503dfd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conversations', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('conversations', 'updated_at')
    # ### end Alembic commands ###
