import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func

from models.database import Base, get_db


class Tweet(Base):
    __tablename__ = "tweet"
    id = Column(Integer, primary_key=True)
    tweet_data = Column(String(500), nullable=False)
    tweet_media_ids = Column(ARRAY(Integer), default=list)
    like = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    users_tweet = relationship("Follower", back_populates="user1")


class Media(Base):
    __tablename__ = "tweet_media"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    content_type = Column(String(500))
    size = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    follower = relationship("Follower", back_populates="user")

class Follower(Base):
    __tablename__ = "followers"
    id = Column(Integer, primary_key=True)
    user1 = Column(Integer, ForeignKey("tweet.id"))
    user2 = Column(Integer, ForeignKey("user.id"))

    tweet = relationship("Tweet", back_populates="users_tweet")
    user = relationship("User", back_populates="follower")

