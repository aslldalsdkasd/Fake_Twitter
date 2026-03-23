from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import engine, session, get_db
from models.models import Base, User
from routes.medias import router as medias_router
from routes.tweets import router as tweets_router
from routes.followed import router as followed_router
from routes.profile import router as profile_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + Shutdown события при запуске API"""
    print("Запуск FastAPI...")
    for i in range(30):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("✅ PostgreSQL готов!")
                break
        except Exception as e:
            print(f"⏳ Попытка {i + 1}/30: {e}")
            await asyncio.sleep(1)

    async with session() as db:
        result = await db.execute(select(User.id).limit(1))
        if not result.scalar_one_or_none():
            user1 = User(name='pipa', id=1, api_key='user1')
            user2 = User(name='pipa2', id=2, api_key='user2')
            db.add_all([user1, user2])
            await db.commit()

        yield

        await engine.dispose()



app = FastAPI(lifespan=lifespan)

app.include_router(tweets_router, prefix="/api", tags=["tweets"])
app.include_router(medias_router, prefix="/api", tags=["medias"])
app.include_router(followed_router, prefix="/api", tags=["followed_tweets"])
app.include_router(profile_router, prefix="/api", tags=["profile"])

# app.mount("/dist", StaticFiles(directory="dist"), name="dist")
# app.mount("/js", StaticFiles(directory="dist/js"), name="js")
# app.mount("/css", StaticFiles(directory="dist/css"), name="css")

@app.get("/index")
async def root():
    """Страница с фронтендом"""
    app.mount("/dist", StaticFiles(directory="dist"), name="dist")
    app.mount("/js", StaticFiles(directory="dist/js"), name="js")
    app.mount("/css", StaticFiles(directory="dist/css"), name="css")
    return FileResponse('dist/index.html')



