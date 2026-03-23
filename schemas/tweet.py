from typing import List, Optional

from pydantic import BaseModel, Field

class TweetCreate(BaseModel):
    tweet_data: str = Field(..., max_length=3000)
    tweet_media_ids: Optional[List[int]] = []

class TweetResponse(BaseModel):
    result: bool
    tweet_id: int



class Author(BaseModel):
    id: int
    name: str

class TweetContext(BaseModel):
    id: int
    content: str
    attachments: List[str]|None
    author: Author
    likes: List[int]


class TweetsTape(BaseModel):
    result: bool
    tweets: List[TweetContext]