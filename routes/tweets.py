from datetime import datetime
from os import getenv
from pathlib import Path
from typing import List, Any

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, Form, File
from sqlalchemy import delete, select
import uuid

from sqlalchemy.orm import selectinload

from database.database import AsyncSession, get_db

from models.models import Tweets, tweet_likes, Media, User
import aiofiles

from schemas.tweet import TweetCreate, TweetResponse, TweetsTape, TweetContext, Author

router = APIRouter()


@router.post("/tweets", status_code=201)
async def tweets(
    request: TweetCreate,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Добавляет новый твит """

    if len(request.tweet_data) > 3000:
        raise HTTPException(status_code=400, detail="Too many tweets")
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if request.tweet_media_ids:
        media_query = await db.execute(
            select(Media.id)
            .where(Media.id.in_(request.tweet_media_ids or []))
        )
        existing_ids = {row[0] for row in media_query.fetchall()}
        missing = set(request.tweet_media_ids) - existing_ids
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing media {missing}")
    tweet = Tweets(
        tweet_data=request.tweet_data,
        tweet_media_ids=request.tweet_media_ids,
        user_id=user.id
    )
    db.add(tweet)
    if db.add:
        tweet.result = True
    await db.commit()
    await db.refresh(tweet)
    return {"tweet_id": tweet.id, "result": True}


@router.delete("/tweets/{id}", status_code=200)
async def delete_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Удаляет твит"""

    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(Tweets).where(Tweets.id == id))
    tweet = result.scalar_one_or_none()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    await db.delete(tweet)
    await db.commit()
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes", status_code=201)
async def like_tweet(
    tweet_id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Ставит лайк на твит"""

    tweet = await db.get(Tweets,tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    existing_like = await db.execute(
        select(tweet_likes)
        .where(tweet_likes.c.user_id == user.id,
               tweet_likes.c.tweet_id == tweet_id
        )
    )
    if existing_like.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tweet already liked")

    ins = tweet_likes.insert().values(
        tweet_id=tweet_id,
        user_id=user.id,)

    await db.execute(ins)
    await db.commit()
    return {"result": True}


@router.delete("/tweets/{id}/likes", status_code=200)
async def unlike_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Убирает лайк с твита"""


    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    existing_like = await db.execute(
        select(tweet_likes)
        .where(tweet_likes.c.tweet_id == id,
            tweet_likes.c.user_id == user.id)
    )
    if not existing_like.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Like not found")

    await db.execute(
        delete(tweet_likes)
        .where(
            tweet_likes.c.tweet_id == id,
            tweet_likes.c.user_id == user.id
        )
    )
    await db.commit()
    return {"result": True}

@router.get("/tweets", response_model=TweetsTape, status_code=200)
async def get_tweets(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db),
) -> TweetsTape:
    """Показывает все твиты пользователя"""
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    stmt =(select(Tweets)
           .where(Tweets.user_id == user.id)
           .options(selectinload(Tweets.user), selectinload(Tweets.likes)))
    result = await db.execute(stmt)
    tweets_rows = result.scalars().all()

    tweets_list = []
    for tweet in tweets_rows:
        media_ids = tweet.tweet_media_ids or []
        attachments = [str(media_id) for media_id in media_ids]

        likes = [t.id for t in tweet.likes]

        tweets_list.append(
            TweetContext(
                id=tweet.id,
                content=tweet.tweet_data,
                attachments=attachments,
                author=Author(
                    id=tweet.user.id,
                    name=tweet.user.name,
                ),
                likes=likes,
            )
        )

    return TweetsTape(result=True, tweets=tweets_list)



