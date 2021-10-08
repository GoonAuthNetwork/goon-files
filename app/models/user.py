from datetime import datetime
from typing import List, Optional
import odmantic
import pydantic

from app.models.service_token import ServiceToken

# Unfortunately we have to duplicate some data models
# because Odmantic doesn't support inheritance, for some reason.
# Also have to use both pydantic and odmantic models seperately.


class User(pydantic.BaseModel):
    userId: int = pydantic.Field(..., title="SA User Id", gt=0)
    userName: str = pydantic.Field(
        ..., title="SA Username", min_length=3, max_length=50, regex="^[\w-_ ]+$"
    )
    regDate: datetime = pydantic.Field(..., title="SA register date")
    permaBanned: Optional[datetime] = pydantic.Field(
        None, title="Date of if/when the user is permanently banned on SA"
    )
    services: Optional[List[ServiceToken]] = pydantic.Field(
        None, title="List of autentication services for the user"
    )
    createdAt: datetime


class UserInDb(odmantic.Model):
    userId: int = odmantic.Field(..., title="SA User Id", gt=0)
    userName: str = odmantic.Field(
        ..., title="SA Username", min_length=3, max_length=50, regex="^[\w-_ ]+$"
    )
    regDate: datetime = odmantic.Field(..., title="SA register date")
    permaBanned: Optional[datetime] = odmantic.Field(
        None, title="Date of if/when the user is permanently banned on SA"
    )
    services: Optional[List[ServiceToken]] = odmantic.Field(
        None, title="List of autentication services for the user"
    )

    # Db Specific
    # hashed_password: str
    # api_token: str
    # etc

    def to_basic_user(self) -> User:
        """Converts the object into a basic pydantic User model

        Returns:
            User: The basic user model
        """
        return User(**self.dict(), createdAt=self.id.generation_time)


class NewUser(pydantic.BaseModel):
    userId: int = pydantic.Field(..., title="SA User Id", gt=0)
    userName: str = pydantic.Field(
        ..., title="SA Username", min_length=3, max_length=50, regex="^[\w-_ ]+$"
    )
    regDate: datetime = pydantic.Field(..., title="SA register date")
    services: Optional[List[ServiceToken]] = pydantic.Field(
        None, title="List of autentication services for the user"
    )
