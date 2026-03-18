from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
from database.database import engine
from models.models import Base
from routes.medias import router as medias_router
from routes.tweets import router as tweets_router
from routes.followed import router as followed_router
from routes.profile import router as profile_router

app = FastAPI()

app.include_router(tweets_router, prefix="/api", tags=["tweets"])
app.include_router(medias_router, prefix="/api", tags=["medias"])
app.include_router(followed_router, prefix="/api", tags=["followed_tweets"])
app.include_router(profile_router, prefix="/api", tags=["profile"])

app.mount('/dist', StaticFiles(directory='dist'), name='dist')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + Shutdown события"""
    print("Запуск FastAPI...")
    for i in range(30):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("PostgreSQL готов! Таблицы созданы!")
                break
        except Exception as e:
            print(f"PostgreSQL не готов, попытка {i + 1}/30: {e}")
            await asyncio.sleep(1)
    else:
        print("PostgreSQL не запустился за 30 секунд!")

    yield


    await engine.dispose()
    print(" FastAPI остановлен")


app.router.lifespan_context = lifespan


@app.get("/")
async def root():
    return {"message": "Fake Twitter API "}