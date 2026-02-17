
from sqlalchemy.ext.asyncio import create_async_engine,  AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine('postgresql+asyncpg://admin:admin@postgres:5432/twitter_db')
Base = declarative_base()

AsyncSession = sessionmaker(engine,
                            expire_on_commit=False,
                            class_=AsyncSession)


async def get_db():
    async with AsyncSession() as session:
        yield session
