from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..models.user import NewUser, User, UserInDb
from ..models.service_token import Service, ServiceToken, NewServiceToken
from ..mongodb import db

router = APIRouter(prefix="/user", tags=["auth"])


@router.post(
    "/",
    response_model=User,
    summary="Creates a User with the specified information",
)
async def create_user(new_user: NewUser) -> User:
    # Check to make sure the user doesn't already exist
    found = await db.engine.find_one(UserInDb, UserInDb.userId == new_user.userId)

    if found:
        raise HTTPException(409, "User already exists")

    # add in hashed_password, etc eventually
    user: UserInDb = UserInDb(**new_user.dict())

    new_user: UserInDb = await db.engine.save(user)

    return new_user.to_basic_user()


@router.get(
    "/{user_id}",
    response_model=User,
    summary="Gets a User for the specified user",
)
async def get_user(user_id: int) -> User:
    user: UserInDb = await db.engine.find_one(UserInDb, UserInDb.userId == user_id)

    if user is None:
        raise HTTPException(404, "User not found")

    return user.to_basic_user()


@router.get(
    "/{user_id}/service",
    response_model=ServiceToken,
    summary="Gets an ServiceToken for the specified user and service",
)
async def get_service_for_user(user_id: int, service: Service) -> ServiceToken:
    query = {"userId": {"$eq": user_id}, "services.service": {"$eq": service.value}}
    user: UserInDb = await db.engine.find_one(UserInDb, query)

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
    user: UserInDb = await db.engine.find(UserInDb, UserInDb.userId == user_id)

    # Check if we're updating
    for i in range(len(user.services)):
        if user.services[i].service == authtoken.service:
            user.services[i] = authtoken
            return await db.engine.save(user)

    # Or else add it
    user.services.append(authtoken)
    result: UserInDb = await db.engine.save(user)

    return result.to_basic_user()
