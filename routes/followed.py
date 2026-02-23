

from mypy.dmypy.client import request

from models.database import AsyncSession, get_db
from routes.medias import SECRET_KEY
from models.db_orm import Follower
from fastapi import APIRouter, Depends, Header, HTTPException

router = APIRouter()

@router.post('/users/<id>/follow')
async def user_follow(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)
):
    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute('INSERT INTO followers ')

