from fastapi import FastAPI
from sqlalchemy.util import asyncio

from models.database import Base, engine
from routes.medias import router as medias_router
from routes.tweets import router as tweets_router

app = FastAPI()

app.include_router(tweets_router, prefix="/api", tags=["tweets"])
app.include_router(medias_router, prefix="/api", tags=["medias"])


@app.on_event("startup")
async def startup():
    """Ждем PostgreSQL + создаем таблицы"""
    for i in range(30):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print(" Таблицы созданы!")
                return
        except Exception as e:
            print(f" PostgreSQL не готов, попытка {i + 1}/30: {e}")
            await asyncio.sleep(1)

    print("❌ PostgreSQL не запустился за 30 секунд!")


@app.get("/")
async def root():
    return {"message": "Hello World"}
