from datetime import datetime
from os import getenv
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, Form, File
from sqlalchemy import delete, select
import uuid

from sqlalchemy.testing import in_

from database.database import AsyncSession, get_db
from func.search_user_id import search_user_id
from models.models import Tweets, tweet_likes, Media, User
import aiofiles

from schemas.tweet import TweetCreate, TweetResponse, TweetsTape

router = APIRouter()


@router.post("/tweets", response_model=TweetResponse)
async def tweets(
    request: TweetCreate,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):

    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if len(request.tweet_data) > 3000:
        raise HTTPException(status_code=400, detail="Too many tweets")

    if request.tweet_media_ids:
        media_query = await db.execute(
            select(Media.id)
            .where(Media.id,in_(request.tweet_media_ids))
        )
        existing_ids = {row[0] for row in media_query.fetchall()}
        missing = set(request.tweet_media_ids) - existing_ids
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing media {missing}")
    tweet = Tweets(
        body=request.tweet_data,
        tweet_media_ids=request.tweet_media_ids,
    )
    db.add(tweet)
    if db.add:
        tweet.result = True
    await db.commit()
    await db.refresh(tweet)
    return {"id": tweet.id, "result": tweet.result}


@router.delete("/tweets/{id}")
async def delete_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):

    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(Tweets).where(Tweets.id == id))
    tweet = result.scalar_one_or_none()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    await db.delete(tweet)
    await db.commit()
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes")
async def like_tweet(
    tweet_id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):
    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    tweet = await db.get(Tweets,tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    user_id = search_user_id(api_key)
    existing_like = await db.execute(
        select(tweet_likes)
        .where(tweet_likes.c.user_id == user_id,
               tweet_likes.c.tweet_id == tweet_id
        )
    )
    if existing_like.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tweet already liked")

    ins = tweet_likes.insert().values(
        tweet_id=tweet_id,
        user_id=user_id,)
    await db.execute(ins)
    await db.commit()
    return {"result": True}


@router.delete("/tweets/{id}/likes")
async def unlike_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):
    if api_key != getenv('SECRET_KEY'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = search_user_id(api_key)
    existing_like = await db.execute(
        select(tweet_likes)
        .where(tweet_likes.c.tweet_id == id,
            tweet_likes.c.user_id == user_id)
    )
    if existing_like.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Like not found")

    await db.execute(
        delete(tweet_likes)
        .where(
            tweet_likes.c.tweet_id == id,
            tweet_likes.c.user_id == user_id
        )
    )
    await db.commit()
    return {"result": True}

@router.get("/tweets", response_model=TweetsTape)
async def get_tweets(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db),
):
    user = search_user_id(api_key)
    result = await db.execute(
        select(Tweets).where(Tweets.user_id == user)
    )
    tweets_db = result.scalars().all()
    likes = select(tweet_likes).where(tweet_likes.c.user_id == user).all()
    tweets_response = []
    for tweet in tweets_db:
        tweet_response = Tweets(
            id=tweet.id,
            content=tweet.tweet_data,
            attachments=List[tweet.tweet_media_ids],
            author=User(id=tweet.user_id, name=tweet.user.name),
            likes=List[likes]
        )
        tweets_response.append(tweet_response)

    return TweetsTape(result=True, tweets=tweets_response)


