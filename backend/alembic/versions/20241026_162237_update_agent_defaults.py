"""update_agent_defaults

Revision ID: 660d0da9861d
Revises: 7702873a4bf3
Create Date: 2024-10-26 16:22:37.222487

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '660d0da9861d'
down_revision: Union[str, None] = '7702873a4bf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop tables in correct order (child tables first)
    op.drop_index('ix_messages_id', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('ix_conversations_id', table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('ix_tts_voice_preferences_id', table_name='tts_voice_preferences')
    op.drop_table('tts_voice_preferences')

    # Add default values to existing agents table
    op.alter_column('agents', 'provider',
        server_default='openai',
        existing_type=sa.String(),
        nullable=False)
    
    op.alter_column('agents', 'model',
        server_default='gpt-4o-mini',
        existing_type=sa.String(),
        nullable=False)
    
    op.alter_column('agents', 'voice',
        server_default='alloy',
        existing_type=sa.String(),
        nullable=True)
    
    # Update existing rows to use new defaults
    op.execute("""
        UPDATE agents 
        SET provider = 'openai', 
            model = 'gpt-4o-mini',
            voice = 'alloy'
        WHERE provider IS NULL 
           OR model IS NULL 
           OR voice IS NULL
    """)


def downgrade() -> None:
    # Remove default values from agents table
    op.alter_column('agents', 'provider',
        server_default=None,
        existing_type=sa.String(),
        nullable=True)
    
    op.alter_column('agents', 'model',
        server_default=None,
        existing_type=sa.String(),
        nullable=True)
    
    op.alter_column('agents', 'voice',
        server_default=None,
        existing_type=sa.String(),
        nullable=True)

    # Recreate tables in correct order (parent tables first)
    op.create_table('tts_voice_preferences',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('voice', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('speed', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column('model', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='tts_voice_preferences_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='tts_voice_preferences_pkey'),
        sa.UniqueConstraint('user_id', name='tts_voice_preferences_user_id_key')
    )
    op.create_index('ix_tts_voice_preferences_id', 'tts_voice_preferences', ['id'], unique=False)

    op.create_table('conversations',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='conversations_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='conversations_pkey')
    )
    op.create_index('ix_conversations_id', 'conversations', ['id'], unique=False)

    op.create_table('messages',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('media_type', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('media_url', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='messages_conversation_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='messages_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='messages_pkey')
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
