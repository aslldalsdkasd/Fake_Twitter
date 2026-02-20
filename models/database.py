from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://admin:admin@postgres:5432/twitter_db"
)
Base = declarative_base()

AsyncSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSession() as session:
        yield session
