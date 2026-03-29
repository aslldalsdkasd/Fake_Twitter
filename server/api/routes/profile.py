
from fastapi import APIRouter, Header, Depends, HTTPException
from server.api.database.database import AsyncSession, get_db

from sqlalchemy import select


from server.api.models.models import User, user_followers
from server.api.schemas.profile import FollowersShema, Profile, UserSchema

DETAIL_UNAUTHORIZED = "Unauthorized"
STATUS_CREATED = 201
STATUS_NOT_FOUND = 404
STATUS_OK = 200

router = APIRouter()


@router.get("/users/me", response_model=Profile, status_code=STATUS_OK)
async def me_profile(
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> Profile:
    """Показывает твою страницу профиля"""

    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=DETAIL_UNAUTHORIZED)

    following_q = await db.execute(
        select(user_followers.c.follower_id).where(user_followers.c.user_id == user.id)
    )
    followers_ids = [row[0] for row in following_q.fetchall()]

    followers_row = await db.execute(
        select(User.id, User.name).where(User.id.in_(followers_ids))
    )

    followers_response = [
        FollowersShema(id=row[0], name=row[1]) for row in followers_row.all()
    ]
    user_response = UserSchema(
        id=user.id,
        name=user.name,
        followers=followers_response,
    )

    return Profile(result=True, user=user_response)


@router.get("/users/{id}", response_model=Profile, status_code=STATUS_OK)
async def user_profile(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> Profile:
    """Показывает чужую страницу профиля"""
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=DETAIL_UNAUTHORIZED)

    user_stmt = select(User).where(User.id == id)
    res = await db.execute(user_stmt)
    user_search = res.scalar_one_or_none()
    if not user_search:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=DETAIL_UNAUTHORIZED)

    following_q = await db.execute(
        select(user_followers.c.follower_id).where(user_followers.c.user_id == id)
    )
    following_ids = [row[0] for row in following_q.fetchall()]

    following_row = await db.execute(
        select(User.id, User.name).where(User.id.in_(following_ids))
    )

    followers_response = [
        FollowersShema(id=row[0], name=row[1]) for row in following_row.all()
    ]
    user_response = UserSchema(
        id=user_search.id,
        name=user_search.name,
        followers=followers_response,
    )

    return Profile(result=True, user=user_response)
