from typing import List, Optional

from pydantic import BaseModel, Field

class TweetCreate(BaseModel):
    tweet_data: str = Field(..., max_length=3000)
    tweet_media_ids: Optional[List[int]] = None

class TweetResponse(BaseModel):
    result: bool
    media_id: int
class Likes(BaseModel):
    user_id: int
    name: str

class Author(BaseModel):
    id: int
    name: str

class Tweet(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: Author
    likes: List[Likes]


class TweetsTape(BaseModel):
    result: bool
    tweets: List[Tweet]