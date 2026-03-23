


from os import getenv

from mypy.error_formatter import JSONFormatter

from database.database import AsyncSession, get_db

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, insert, delete

from func.search_user_id import search_user_id
from models.models import User, user_followers

router = APIRouter()

@router.post('/users/<id>/follow', status_code=201)
async def user_follow(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    """Пользователь подписывается на другого пользователя"""

    target_user = await db.get(User, id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_follow = await db.execute(
        select(user_followers)
        .where(user_followers.c.user_id == user.id,
               user_followers.c.follower_id == id)
    )
    if existing_follow.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User followed already exists")

    await db.execute(
        insert(user_followers).values(
            user_id=user.id,
            follower_id=id,
        )
    )
    await db.commit()
    return {"result": True}


@router.delete('/users/<id>/follow', status_code=200)
async def user_unfollow(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    """Пользователь отписывается от другого пользователя"""

    target_user = await db.get(User, id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await db.execute(stmt)
    existing_follow = await db.execute(
        select(user_followers)
        .where(user_followers.c.user_id == user.id,
               user_followers.c.follower_id == id)
    )
    if not existing_follow.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Not following user")

    await db.execute(
        delete(user_followers)
        .where(user_followers.c.user_id == user.id,
               user_followers.c.follower_id == id)
    )
    await db.commit()

    return {"result": True}