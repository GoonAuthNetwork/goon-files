from fastapi import APIRouter

from app.models.error import ApiError
from app.models.user import NewUser, User, UserInDb
from app.models.service_token import Service, ServiceToken, NewServiceToken
from app.mongodb import db

router = APIRouter(prefix="/user", tags=["auth"])


@router.post(
    "/",
    summary="Creates a User with the specified information",
    response_model=User,
    responses={409: {"model": ApiError, "description": "User Creation Error"}},
)
async def create_user(new_user: NewUser) -> User:
    # Check to make sure the user doesn't already exist
    found = await db.engine.find_one(UserInDb, UserInDb.userId == new_user.userId)

    if found:
        return ApiError.create_response(409, "User already exists")

    # add in hashed_password, etc eventually
    user: UserInDb = UserInDb(**new_user.dict())

    new_user: UserInDb = await db.engine.save(user)

    return new_user.to_basic_user()


@router.get(
    "/",
    summary="Finds a user with the specified service and token",
    response_model=User,
    responses={404: {"model": ApiError, "description": "User Query Error"}},
)
async def find_user(service: Service, token: str) -> User:
    def sanitize(text: str) -> str:
        # TODO: This should cover most of the ways to inject mongo, make better later
        return text.lstrip("$")

    query = {
        "services.service": {"$eq": sanitize(service.value)},
        "services.token": {"$eq": sanitize(token)},
    }

    user: UserInDb = await db.engine.find_one(UserInDb, query)

    if user is None:
        return ApiError.create_response(404, "User not found")

    return user.to_basic_user()


@router.get(
    "/{user_id}",
    summary="Gets a User for the specified user",
    response_model=User,
    responses={404: {"model": ApiError, "description": "User Query Error"}},
)
async def get_user(user_id: int) -> User:
    user: UserInDb = await db.engine.find_one(UserInDb, UserInDb.userId == user_id)

    if user is None:
        return ApiError.create_response(404, "User not found")

    return user.to_basic_user()


@router.get(
    "/{user_id}/service",
    summary="Gets an ServiceToken for the specified user and service",
    response_model=ServiceToken,
    responses={404: {"model": ApiError, "description": "Query Error"}},
)
async def get_service_for_user(user_id: int, service: Service) -> ServiceToken:
    # query = {"userId": {"$eq": user_id}, "services.service": {"$eq": service.value}}
    # user: UserInDb = await db.engine.find_one(UserInDb, query)
    user: UserInDb = await db.engine.find_one(UserInDb, UserInDb.userId == user_id)

    if user is None:
        return ApiError.create_response(404, "User not found")

    for _service in user.services:
        if _service.service == service:
            return _service

    return ApiError.create_response(404, "Service not found for specified user")


@router.put(
    "/{user_id}/service",
    summary="Adds an AuthToken to the User",
    response_model=User,
    responses={404: {"model": ApiError, "description": "Query Error"}},
)
async def add_service_to_user(user_id: int, new_authtoken: NewServiceToken) -> User:
    # pull the user
    user: UserInDb = await db.engine.find_one(UserInDb, UserInDb.userId == user_id)

    if user is None:
        return ApiError.create_response(404, "User not found")

    # Create the auth token
    authtoken: ServiceToken = ServiceToken(
        service=new_authtoken.service, token=new_authtoken.token
    )

    if "info" in new_authtoken and len(new_authtoken.info) > 0:
        authtoken.info = new_authtoken.info

    # Check if we're updating
    for i in range(len(user.services)):
        if user.services[i].service == authtoken.service:
            user.services[i] = authtoken
            saved_user = await db.engine.save(user)
            return saved_user.to_basic_user()

    # Or else add it
    user.services.append(authtoken)
    result: UserInDb = await db.engine.save(user)

    return result.to_basic_user()
