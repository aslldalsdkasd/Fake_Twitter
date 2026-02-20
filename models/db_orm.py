import datetime

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
    like = Column(Boolean, default=None)
    created_at = Column(DateTime, server_default=func.now())


class Media(Base):
    __tablename__ = "tweet_media"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    content_type = Column(String(500))
    size = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
