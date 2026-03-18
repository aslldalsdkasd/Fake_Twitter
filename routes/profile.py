from http.client import HTTPException

from fastapi import APIRouter, Header, Depends, HTTPException
from database.database import AsyncSession, get_db
from os import getenv

from sqlalchemy import select

from func.search_user_id import search_user_id
from models.models import User, user_followers
from schemas.profile import Followers, Profile

router = APIRouter()

@router.get("/users/me", response_model=Profile)
async def me_profile(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db),
):
    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = search_user_id(api_key)

    user_db = await  db.get(User, user)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    following_result = await db.execute(
        select(user_followers.c.follower_id).where(
            user_followers.c.user_id == user
        )
    )

    followers = [
        Followers(id=row[0], name=row[1])
        for row in following_result.fetchall()
    ]
    user_response = User(
        id=user_db.id,
        name=user_db.name,
        followers=followers,
    )

    return Profile(result=True, user=user_response)

@router.get("/users/<id>", response_model=Profile)
async def user_profile(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db),
):
    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_db = await  db.get(User, id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    following_result = await db.execute(
        select(user_followers.c.follower_id).where(
            user_followers.c.user_id == id
        )
    )

    followers = [
        Followers(id=row[0], name=row[1])
        for row in following_result.fetchall()
    ]
    user_response = User(
        id=user_db.id,
        name=user_db.name,
        followers=followers,
    )

    return Profile(result=True, user=user_response)