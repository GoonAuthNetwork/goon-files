from datetime import datetime

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
import pytest

from app.main import app
from app.models.service_token import Service, ServiceToken
from app.models.user import NewUser, UserInDb
from app.mongodb import db, connect_to_mongo, close_mongo_connection

seed_users = [
    UserInDb(
        userId=42069,
        userName="Goon 1",
        services=[ServiceToken(service=Service.DISCORD, token="Goon1#42069")],
        regDate=datetime.now(),
    ),
    UserInDb(
        userId=42070,
        userName="Goon 2",
        services=[ServiceToken(service=Service.DISCORD, token="Goon2#42070")],
        regDate=datetime.now(),
    ),
    UserInDb(
        userId=42071,
        userName="Goon 3",
        services=[ServiceToken(service=Service.DISCORD, token="Goon3#42071")],
        regDate=datetime.now(),
        permaBanned=datetime.now(),
    ),
]


# Per test db state
async def clear_db():
    await connect_to_mongo()

    # Drop collection, here's hoping we're on a test db!
    await db.engine.get_collection(UserInDb).drop()

    await close_mongo_connection()


async def seed_db():
    await connect_to_mongo()

    await db.engine.save_all(seed_users)

    await close_mongo_connection()


@pytest.fixture()
async def seed_test_db():
    await clear_db()
    await seed_db()

    yield

    await clear_db()


@pytest.fixture()
async def async_client(seed_test_db):
    async with AsyncClient(app=app, base_url="http://test") as client, LifespanManager(
        app
    ):
        yield client


@pytest.mark.asyncio
async def test_something(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello root"}


@pytest.mark.asyncio
async def test_new_user_already_exists(async_client):
    # As of right now this should contain more than enough data for a NewUser
    new_user = NewUser(**seed_users[0].dict())

    response = await async_client.post(
        "/user/", content=new_user.json(), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_new_user(async_client):
    new_user = NewUser(
        userId=420,
        userName="Some Cool Guy",
        regDate=datetime.now(),
        services=[ServiceToken(service=Service.DISCORD, token="Some Cool Guy#420")],
    )

    response = await async_client.post(
        "/user/", content=new_user.json(), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    assert all(
        response.json().get(key, None) == val
        for key, val in {
            "permaBanned": None,
            "userId": 420,
            "userName": "Some Cool Guy",
        }.items()
    )
