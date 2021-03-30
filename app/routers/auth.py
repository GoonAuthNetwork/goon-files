from datetime import datetime
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..models.user import User
from ..models.authtoken import AuthToken, Service
from ..mongodb import db

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post(
    "/",
    response_model=User,
    response_model_exclude={"id"},
    summary="Creates a User with the specified information",
)
async def create_user():
    pass


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
    response_model=AuthToken,
    summary="Gets an AuthToken for the specified user and service",
)
async def get_service_for_user(user_id: int, service: Service) -> AuthToken:
    query = {"userId": {"$eq": user_id}, "services.service": {"$eq": service.value}}
    user = await db.engine.find_one(User, query)

    if user is None:
        raise HTTPException(404, "User not found")

    for _service in user.services:
        if _service.service == service:
            return _service

    raise HTTPException(404, "Service not found for specified user")
