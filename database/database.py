from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from os import getenv
from dotenv import load_dotenv
load_dotenv()

engine = create_async_engine('postgresql+asyncpg://admin:admin@postgres:5432/twitter_db')
# engine = create_async_engine(
#     url='postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'.format(
#         DB_USER=getenv('DB_USER'),
#         DB_PASSWORD=getenv('DB_PASSWORD'),
#         DB_HOST=getenv('DB_HOST'),
#         DB_PORT=getenv('DB_PORT'),
#         DB_DATABASE=getenv('DB_DATABASE')
#     )

session = async_sessionmaker(engine, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db_session:
        yield db_session
