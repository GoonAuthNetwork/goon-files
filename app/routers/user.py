from datetime import datetime
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..models.user import NewUser, User
from ..models.service_token import Service, ServiceToken, NewServiceToken
from ..mongodb import db

router = APIRouter(prefix="/user", tags=["auth"])

"""
@router.get("/")
async def root_auth():

    instances = [
        User(
            userId=42069,
            userName="Goon 1",
            services=[AuthToken(service=Service.DISCORD, token="Goon1#42069")],
            regDate=datetime.now(),
            createdAt=datetime.now(),
        ),
        User(
            userId=42070,
            userName="Goon 2",
            services=[AuthToken(service=Service.DISCORD, token="Goon2#42070")],
            regDate=datetime.now(),
            createdAt=datetime.now(),
        ),
        User(
            userId=42071,
            userName="Goon 3",
            services=[AuthToken(service=Service.DISCORD, token="Goon3#42071")],
            regDate=datetime.now(),
            createdAt=datetime.now(),
        ),
    ]
    await db.engine.save_all(instances)

    return {"message": "Hello auth"}
"""


@router.post(
    "/",
    response_model=User,
    response_model_exclude={"id"},
    summary="Creates a User with the specified information",
)
async def create_user(new_user: NewUser) -> User:
    user: User = User(
        userId=new_user.userId,
        userName=new_user.userName,
        regDate=new_user.regDate,
        createdAt=datetime.now(),
    )

    if "services" in new_user and len(new_user.services) > 0:
        user.services = new_user.services

    return await db.engine.save(user)


@router.get(
    "/{user_id}",
    response_model=User,
    response_model_exclude={"id"},
    summary="Gets a User for the specified user",
)
async def get_user(user_id: int) -> User:
    user = await db.engine.find_one(User, User.userId == user_id)

    if user is None:
        raise HTTPException(404, "User not found")

    return user


@router.get(
    "/{user_id}/service",
    response_model=ServiceToken,
    summary="Gets an ServiceToken for the specified user and service",
)
async def get_service_for_user(user_id: int, service: Service) -> ServiceToken:
    query = {"userId": {"$eq": user_id}, "services.service": {"$eq": service.value}}
    user = await db.engine.find_one(User, query)

    if user is None:
        raise HTTPException(404, "User not found")

    for _service in user.services:
        if _service.service == service:
            return _service

    raise HTTPException(404, "Service not found for specified user")


@router.put(
    "/{user_id}/service", response_model=User, summary="Adds an AuthToken to the User"
)
async def add_service_for_user(user_id: int, new_authtoken: NewServiceToken) -> User:
    # Create the auth token
    authtoken: ServiceToken = ServiceToken(
        service=new_authtoken.service, token=new_authtoken.token
    )

    if "info" in new_authtoken and len(new_authtoken.info) > 0:
        authtoken.info = new_authtoken.info

    # pull the user
    user: User = await db.engine.find(User, User.userId == user_id)

    # Check if we're updating
    for i in range(len(user.services)):
        if user.services[i].service == authtoken.service:
            user.services[i] = authtoken
            return await db.engine.save(user)

    # Or else add it
    user.services.append(authtoken)
    return await db.engine.save(user)
