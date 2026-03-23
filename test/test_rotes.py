from io import BytesIO

import pytest
import pytest_asyncio
import httpx
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.database import get_db
from models.models import User, Tweets, user_followers, Base, tweet_likes
from fast_app import app


@pytest.fixture(scope="function")
def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        user1 = User(id=1, name="pipa", api_key="user1")
        user2 = User(id=2, name="pipa2", api_key="user2")
        tweet1 = Tweets(id=1, user_id=1, tweet_data="Hello world111!")
        tweet2 = Tweets(id=2, user_id=2, tweet_data="Hello world222!")

        await session.execute(tweet_likes.insert().values(tweet_id=1, user_id=2))
        await session.execute(user_followers.insert().values(user_id=1, follower_id=2))
        session.add_all([user1, user2, tweet1, tweet2])
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_tweets(client):
    response = await client.get("/api/tweets", headers={"api-key": "user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == True
    assert data["tweets"][0]["id"] == 1
    assert len(data["tweets"]) == 1
    assert data["tweets"][0]["content"] == "Hello world111!"
    assert data["tweets"][0]["attachments"] == []
    assert data["tweets"][0]["author"]["id"] == 1
    assert data["tweets"][0]["author"]["name"] == "pipa"
    assert data["tweets"][0]["likes"] == [2]


@pytest.mark.asyncio
async def test_profile_me(client):
    response = await client.get("/api/users/me", headers={"api-key": "user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "pipa"
    assert data["user"]["followers"][0]["id"] == 2
    assert data["user"]["followers"][0]["name"] == "pipa2"
    assert len(data["user"]) == 3


@pytest.mark.asyncio
async def test_profile_user_id(client):
    response = await client.get("/api/users/1", headers={"api-key": "user2"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "pipa"
    assert data["user"]["followers"][0]["id"] == 2
    assert data["user"]["followers"][0]["name"] == "pipa2"
    assert len(data["user"]) == 3


@pytest.mark.asyncio
async def test_tweet_post(client):
    response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        json={"tweet_data": "Hello world111!", "tweet_media_ids": []},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == True
    assert data["tweet_id"] == 3


@pytest.mark.asyncio
async def test_wrong_type_post(client):
    response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        data={"tweet_data": "Hello world111!", "tweet_media_ids": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_no_existing_media(client):
    response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        json={"tweet_data": "Hello world111!", "tweet_media_ids": [1, 2]},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Missing media {1, 2}"


@pytest.mark.asyncio
async def test_create_and_delete_tweet(client):
    create_response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        json={"tweet_data": "Hello world111!", "tweet_media_ids": []},
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["result"] == True
    assert data["tweet_id"] == 3

    get_tweet_response = await client.get(f"/api/tweets", headers={"api-key": "user1"})
    assert get_tweet_response.status_code == 200
    data = get_tweet_response.json()
    assert data["result"] == True
    assert data["tweets"][1]["id"] == 3
    assert data["tweets"][1]["author"]["id"] == 1
    assert data["tweets"][1]["author"]["name"] == "pipa"
    assert data["tweets"][1]["content"] == "Hello world111!"
    assert data["tweets"][1]["attachments"] == []
    assert len(data["tweets"]) == 2
    delete_response = await client.delete(
        f"/api/tweets/3", headers={"api-key": "user1"}
    )
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["result"] == True

    get_tweet_response = await client.get(f"/api/tweets", headers={"api-key": "user1"})
    assert get_tweet_response.status_code == 200
    data = get_tweet_response.json()
    assert data["result"] == True
    assert len(data["tweets"]) == 1


@pytest.mark.asyncio
async def test_liked_and_unliked_tweet(client):
    liked_response = await client.post(
        "/api/tweets/2/likes", headers={"api-key": "user1"}
    )
    assert liked_response.status_code == 201
    data = liked_response.json()
    assert data["result"] == True

    liked_check_response = await client.get("/api/tweets", headers={"api-key": "user2"})
    assert liked_check_response.status_code == 200
    data = liked_check_response.json()
    assert data["result"] == True
    assert data["tweets"][0]["id"] == 2
    assert data["tweets"][0]["likes"] == [1]

    unliked_response = await client.delete(
        "/api/tweets/2/likes", headers={"api-key": "user1"}
    )
    assert unliked_response.status_code == 200
    data = unliked_response.json()
    assert data["result"] == True

    unliked_check_response = await client.get(
        "/api/tweets", headers={"api-key": "user2"}
    )
    assert unliked_check_response.status_code == 200
    data = unliked_check_response.json()
    assert data["result"] == True
    assert data["tweets"][0]["id"] == 2
    assert data["tweets"][0]["likes"] == []


@pytest.mark.asyncio
async def test_following_and_unfollowed_user(client):
    following_response = await client.post(
        "/api/users/1/follow", headers={"api-key": "user2"}
    )
    assert following_response.status_code == 201
    data = following_response.json()
    assert data["result"] == True

    following_response_check = await client.get(
        "/api/users/me", headers={"api-key": "user1"}
    )
    assert following_response_check.status_code == 200
    data = following_response_check.json()
    assert data["result"] == True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "pipa"
    assert data["user"]["followers"][0]["id"] == 2
    assert data["user"]["followers"][0]["name"] == "pipa2"

    unfollowing_response = await client.delete(
        "/api/users/1/follow", headers={"api-key": "user2"}
    )
    assert unfollowing_response.status_code == 200
    data = unfollowing_response.json()
    assert data["result"] == True

    unfollowing_response_check = await client.get(
        "/api/users/me", headers={"api-key": "user1"}
    )
    assert unfollowing_response_check.status_code == 200
    data = unfollowing_response_check.json()
    assert data["result"] == True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "pipa"
    assert data["user"]["followers"] == []


@pytest.mark.asyncio
async def test_add_media(client):
    image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x78\x00\x00\x00\x00IEND\xaeB`\x82"
    response = await client.post(
        "/api/medias",
        headers={"api-key": "user1"},
        files={"file": ("test.png", BytesIO(image_data), "image/png")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == True
    assert data["media_id"] == 1

    add_tweet_response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        json=({"tweet_data": "hello", "tweet_media_ids": [1]}),
    )
    assert add_tweet_response.status_code == 201
    data = add_tweet_response.json()
    assert data["result"] == True

    chek_tweet_response = await client.get("/api/tweets", headers={"api-key": "user1"})
    assert chek_tweet_response.status_code == 200
    data = chek_tweet_response.json()
    assert data["result"] == True
    assert data["tweets"][1]["id"] == 3
    assert data["tweets"][1]["attachments"] == ["1"]
    assert data["tweets"][1]["content"] == "hello"
    assert data["tweets"][1]["author"]["id"] == 1
    assert data["tweets"][1]["author"]["name"] == "pipa"


@pytest.mark.asyncio
async def test_chek_unautorized_user(client):
    tweet_get_response = await client.get("/api/tweets", headers={"api-key": "112"})
    assert tweet_get_response.status_code == 401
    data = tweet_get_response.json()
    assert data["detail"] == "Unauthorized"

    user_profile_response = await client.get("/api/users/1", headers={"api-key": "dd"})
    assert user_profile_response.status_code == 404
    data = user_profile_response.json()
    assert data["detail"] == "Unauthorized"

    user_me_response = await client.get("/api/users/1", headers={"api-key": "dd"})
    assert user_me_response.status_code == 404
    data = user_me_response.json()
    assert data["detail"] == "Unauthorized"

    tweet_post_response = await client.post(
        "/api/tweets",
        headers={"api-key": "dd"},
        json={"tweet_data": "Hello world111!", "tweet_media_ids": []},
    )
    data = tweet_post_response.json()
    assert tweet_post_response.status_code == 401
    assert data["detail"] == "Unauthorized"
