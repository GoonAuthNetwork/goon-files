from datetime import datetime
import random
import urllib.parse

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
import pytest

from app.main import app
from app.models.service_token import NewServiceToken, Service, ServiceToken
from app.models.user import NewUser, User, UserInDb
from app.mongodb import db, connect_to_mongo, close_mongo_connection

from .utils import generate_username, is_sub_dict

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
async def test_something(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello root"}


@pytest.mark.asyncio
async def test_new_user_already_exists(async_client: AsyncClient):
    # As of right now this should contain more than enough data for a NewUser
    user = random.choice(seed_users)
    new_user = NewUser(**user.dict())

    response = await async_client.post(
        "/user/", content=new_user.json(), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 409
    assert response.json() == {"message": "User already exists"}


@pytest.mark.asyncio
async def test_new_user(async_client: AsyncClient):
    name = generate_username()
    new_user = NewUser(
        userId=420,
        userName=name,
        regDate=datetime.now(),
        services=[ServiceToken(service=Service.DISCORD, token=f"{name}#420")],
    )

    response = await async_client.post(
        "/user/", content=new_user.json(), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    assert is_sub_dict(
        response.json(),
        {
            "permaBanned": None,
            "userId": 420,
            "userName": name,
        },
    )


@pytest.mark.asyncio
async def test_find_user_by_service_not_found(async_client: AsyncClient):
    response = await async_client.get("/user/?service=discord&token=invalid_token")

    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


@pytest.mark.asyncio
async def test_find_user_by_service(async_client: AsyncClient):
    user = random.choice(seed_users)
    service = urllib.parse.quote(user.services[0].service.value)
    token = urllib.parse.quote(user.services[0].token)

    response = await async_client.get(f"/user/?service={service}&token={token}")
    assert response.status_code == 200

    returned_user = User(**response.json())
    assert user.userName == returned_user.userName
    assert user.userId == returned_user.userId


@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient):
    response = await async_client.get("/user/420")

    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    user = random.choice(seed_users)
    response = await async_client.get(f"/user/{user.userId}")
    returned_user = User(**response.json())

    assert response.status_code == 200
    assert user.userName == returned_user.userName


@pytest.mark.asyncio
async def test_get_service_for_user_not_found(async_client: AsyncClient):
    response = await async_client.get("/user/420/service?service=discord")

    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


@pytest.mark.asyncio
async def test_get_service_for_user_service_not_found(async_client: AsyncClient):
    user = random.choice(seed_users)
    response = await async_client.get(f"/user/{user.userId}/service?service=other")

    assert response.status_code == 404
    assert response.json() == {"message": "Service not found for specified user"}


@pytest.mark.asyncio
async def test_get_service_for_user(async_client: AsyncClient):
    user = random.choice(seed_users)
    response = await async_client.get(f"/user/{user.userId}/service?service=discord")

    service = ServiceToken(**response.json())

    assert response.status_code == 200
    assert service in user.services


@pytest.mark.asyncio
async def test_add_service_to_user_not_exist(async_client: AsyncClient):
    token = NewServiceToken(service=Service.OTHER, token="RandomData")

    response = await async_client.put(
        "/user/420/service",
        content=token.json(),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


@pytest.mark.asyncio
async def test_add_service_to_user_update(async_client: AsyncClient):
    user = random.choice(seed_users)
    token = NewServiceToken(service=Service.DISCORD, token="RandomData")

    response = await async_client.put(
        f"/user/{user.userId}/service",
        content=token.json(),
        headers={"Content-Type": "application/json"},
    )

    returned_user = User(**response.json())

    assert response.status_code == 200
    assert user.userName == returned_user.userName
    assert any(x.token == "RandomData" for x in returned_user.services)


@pytest.mark.asyncio
async def test_add_service_to_user_add(async_client: AsyncClient):
    user = random.choice(seed_users)
    token = NewServiceToken(service=Service.OTHER, token="RandomData")

    response = await async_client.put(
        f"/user/{user.userId}/service",
        content=token.json(),
        headers={"Content-Type": "application/json"},
    )

    returned_user = User(**response.json())

    assert response.status_code == 200
    assert user.userName == returned_user.userName
    assert any(
        x.token == "RandomData" and x.service == "other" for x in returned_user.services
    )
