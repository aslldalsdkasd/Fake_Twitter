from typing import List

from pydantic import BaseModel

class Followers(BaseModel):
    id: int
    name: str

class UserSchema(BaseModel):
    id: int
    name: str
    followers: List[Followers]

class Profile(BaseModel):
    result: bool
    user: UserSchema