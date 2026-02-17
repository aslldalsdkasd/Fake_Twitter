from typing import Optional

from pydantic import BaseModel



class MediasResponse(BaseModel):
    media_id: int
    result: bool