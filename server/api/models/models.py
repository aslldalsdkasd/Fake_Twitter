from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    LargeBinary,
    ForeignKey,
    Integer,
    Table,
    JSON,
    String,
    text,
    Column,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

MEDIA_MAX_LENGHT = 500
TWEET_MAX_LENGHT = 3000


class Base(DeclarativeBase):
    pass


tweet_likes = Table(
    "tweet_likes",
    Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

user_followers = Table(
    "user_followers",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)

    # подписки на тебя
    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_followers",
        primaryjoin=user_followers.c.follower_id == id,
        secondaryjoin=user_followers.c.user_id == id,
        back_populates="following",
    )
    # на кого подписан ты
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_followers",
        primaryjoin=user_followers.c.user_id == id,
        secondaryjoin=user_followers.c.follower_id == id,
        back_populates="followers",
    )

    liked_tweets: Mapped[list["Tweets"]] = relationship(
        "Tweets",
        secondary="tweet_likes",
        back_populates="likes",
    )


class Tweets(Base):
    __tablename__ = "tweets"
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_data: Mapped[str] = mapped_column(String(TWEET_MAX_LENGHT), nullable=False)
    tweet_media_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    # created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User")

    likes: Mapped[list["User"]] = relationship(
        "User",
        secondary="tweet_likes",
        back_populates="liked_tweets",
    )


class Media(Base):
    __tablename__ = "medias"
    id: Mapped[int] = mapped_column(primary_key=True)
    filepath: Mapped[str] = mapped_column(String(MEDIA_MAX_LENGHT), nullable=False)
    filename: Mapped[str] = mapped_column(String(MEDIA_MAX_LENGHT), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
