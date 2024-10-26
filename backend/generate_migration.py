import asyncio
from alembic import command
from alembic.config import Config
from app.models import Base
from app.database import engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def generate_migration():
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message="initial migration")

if __name__ == "__main__":
    # Create tables first
    asyncio.run(create_tables())
    # Then generate migration
    generate_migration()
