from typing import List

from pydantic import BaseModel

class FollowersShema(BaseModel):
    id: int
    name: str

class UserSchema(BaseModel):
    id: int
    name: str
    followers: List[FollowersShema]

class Profile(BaseModel):
    result: bool
    user: UserSchema