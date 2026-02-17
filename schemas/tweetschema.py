from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []

class TweetResponse(BaseModel):
    id: int
    result: bool
    class Config:
        orm_mode = True





