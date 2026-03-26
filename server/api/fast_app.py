from pathlib import Path

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
import uvicorn
from sqlalchemy import select
import logging
LOGGER = logging.getLogger(__name__)
UPLOAD_DIR = Path("uploads")
CLIENT_DIST = Path("/app/client/dist")

from server.api.database.database import engine, session
from server.api.models.models import Base, User
from server.api.routes.medias import router as medias_router
from server.api.routes.tweets import router as tweets_router
from server.api.routes.followed import router as followed_router
from server.api.routes.profile import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOGGER.info("Start POSTGRES connection...")


    max_retries = 20
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                LOGGER.info(" POSTGRES TABLES READY")
                break
        except Exception as e:
            if "name resolution" in str(e).lower():
                LOGGER.warning(f" DNS retry {attempt + 1}/{max_retries}: {str(e)[:80]}")
                await asyncio.sleep(2)
            else:
                LOGGER.error(f"Tables error: {e}")
                raise
    else:
        raise RuntimeError("Database initialization timeout")


    for attempt in range(10):
        try:
            async with session() as db:
                result = await db.execute(select(User.id).limit(1))
                if not result.scalar_one_or_none():
                    user1 = User(name="pipa", id=1, api_key="test")
                    user2 = User(name="pipa2", id=2, api_key="user2")
                    db.add_all([user1, user2])
                    await db.commit()
                    LOGGER.info("Users created")
                break
        except Exception as e:
            LOGGER.warning(f"Users retry {attempt + 1}: {str(e)[:80]}")
            await asyncio.sleep(1)

    yield

    await engine.dispose()
    LOGGER.info("POSTGRES disposed")


app = FastAPI(lifespan=lifespan)

app.include_router(tweets_router, prefix="/api", tags=["tweets"])
app.include_router(medias_router, prefix="/api", tags=["medias"])
app.include_router(followed_router, prefix="/api", tags=["followed_tweets"])
app.include_router(profile_router, prefix="/api", tags=["profile"])


@app.middleware("http")
async def check_user_middleware(request: Request, call_next):
    """Middleware for checking user"""
    if request.url.path.startswith("/api") and not request.url.path.startswith("api/medias"):
        async with session() as db:
            key_api = request.headers.get("api-key")
            if not key_api:
                raise HTTPException(status_code=404, detail="api key not found")
            stmt = select(User).where(User.api_key == key_api)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
    response = await call_next(request)
    return response


@app.get("/")
def root():
    """Страница с фронтендом"""
    return FileResponse(CLIENT_DIST / "index.html")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/dist", StaticFiles(directory=CLIENT_DIST), name="dist")
app.mount("/js", StaticFiles(directory=CLIENT_DIST / "js"), name="js")
app.mount("/css", StaticFiles(directory=CLIENT_DIST / "css"), name="css")
