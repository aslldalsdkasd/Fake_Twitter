from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetResponse(BaseModel):
    id: int
    result: bool

    class Config:
        orm_mode = True
