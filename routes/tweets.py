from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import delete, select

from models.database import AsyncSession, get_db
from models.db_orm import Tweet
from routes.medias import SECRET_KEY
from schemas.tweetschema import TweetCreate, TweetResponse

router = APIRouter()


@router.post("/tweets", response_model=TweetResponse)
async def tweets(
    request: TweetCreate,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):

    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if len(request.tweet_data) > 500:
        raise HTTPException(status_code=400, detail="Too many tweets")

    tweet = Tweet(
        tweet_data=request.tweet_data,
        tweet_media_ids=request.tweet_media_ids or [],
        created_at=datetime.now()
    )

    db.add(tweet)
    if db.add:
        tweet.result = True
    await db.commit()
    await db.refresh(tweet)
    return {"id": tweet.id, "result": tweet.result}


@router.delete("/tweets/<id>")
async def delete_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):

    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(Tweet).where(Tweet.id == id))
    tweet = result.scalar_one_or_none()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    await db.delete(tweet)
    await db.commit()
    return {"result": True}


@router.post("/tweets/<id>/likes")
async def like_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):
    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(Tweet).where(Tweet.id == id))
    tweet = result.scalar_one_or_none()
    tweet.likes = True

    return {"result": True}


@router.delete("/tweets/<id>/likes")
async def unlike_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):
    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(Tweet).where(Tweet.id == id))
    tweet = result.scalar_one_or_none()

    tweet.likes = False

    await db.commit()
    await db.refresh(tweet)

    return {"result": True}
