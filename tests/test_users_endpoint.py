from datetime import datetime

from httpx import AsyncClient
import pytest
from _pytest.fixtures import FixtureRequest

from app.main import app
from app.models.service_token import Service, ServiceToken
from app.models.user import UserInDb
from app.mongodb import db, connect_to_mongo, close_mongo_connection


# Per test db state
async def clear_db():
    await connect_to_mongo()

    # Drop collection, here's hoping we're on a test db!
    await db.engine.get_collection(UserInDb).drop()

    await close_mongo_connection()


async def seed_db():
    await connect_to_mongo()

    users = [
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

    await db.engine.save_all(users)

    await close_mongo_connection()


@pytest.fixture()
async def seed_test_db(request: FixtureRequest, event_loop):
    await clear_db()
    await seed_db()

    def fin():
        async def afin():
            await clear_db()

        event_loop.run_until_complete(afin())

    request.addfinalizer(fin)


@pytest.mark.asyncio
async def test_something(seed_test_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello root"}
