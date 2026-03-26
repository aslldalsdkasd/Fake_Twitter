STATUS_CREATED = 201
STATUS_NOT_FOUND = 404
STATUS_OK = 200
MSG_USER_NOT_FOUND = "User not found"


from server.api.database.database import AsyncSession, get_db

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, insert, delete


from server.api.models.models import User, user_followers

router = APIRouter()


@router.post("/users/{id}/follow", status_code=STATUS_CREATED)
async def user_follow(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Пользователь подписывается на другого пользователя"""

    target_user = await db.get(User, id)
    if not target_user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=MSG_USER_NOT_FOUND)

    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=MSG_USER_NOT_FOUND)
    existing_follow = await db.execute(
        select(user_followers).where(
            user_followers.c.user_id == user.id, user_followers.c.follower_id == id
        )
    )
    if existing_follow.scalar_one_or_none():
        raise HTTPException(
            status_code=STATUS_NOT_FOUND, detail="User followed already exists"
        )

    await db.execute(
        insert(user_followers).values(
            user_id=user.id,
            follower_id=id,
        )
    )
    await db.commit()
    return {"result": True}


@router.delete("/users/{id}/follow", status_code=STATUS_OK)
async def user_unfollow(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Пользователь отписывается от другого пользователя"""

    target_user = await db.get(User, id)
    if not target_user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=MSG_USER_NOT_FOUND)
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=MSG_USER_NOT_FOUND)
    result = await db.execute(stmt)
    existing_follow = await db.execute(
        select(user_followers).where(
            user_followers.c.user_id == user.id, user_followers.c.follower_id == id
        )
    )
    if not existing_follow.scalar_one_or_none():
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail="Not following user")

    await db.execute(
        delete(user_followers).where(
            user_followers.c.user_id == id, user_followers.c.follower_id == user.id
        )
    )
    await db.commit()

    return {"result": True}
