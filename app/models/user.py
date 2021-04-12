from datetime import datetime
from typing import List, Optional
import odmantic
import pydantic

from .service_token import ServiceToken


# Unfortunately we have to duplicate some data models
# because Odmantic doesn't support inheritance, for some reason.
# Also have to use both pydantic and odmantic models seperately.


class User(pydantic.BaseModel):
    userId: int = pydantic.Field(..., title="SA User Id", gt=0)
    userName: str = pydantic.Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    regDate: datetime
    permaBanned: Optional[datetime]
    services: Optional[List[ServiceToken]]
    createdAt: datetime


class UserInDb(odmantic.Model):
    userId: int = odmantic.Field(..., title="SA User Id", gt=0)
    userName: str = odmantic.Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    regDate: datetime
    permaBanned: Optional[datetime]
    services: Optional[List[ServiceToken]]

    # Db Specific
    # hashed_password: str
    # api_token: str
    # etc

    def to_basic_user(self) -> User:
        return User(**self.dict(), createdAt=self.id.generation_time)


class NewUser(pydantic.BaseModel):
    userId: int = pydantic.Field(..., title="SA User Id", gt=0)
    userName: str = pydantic.Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    regDate: datetime
    services: Optional[List[ServiceToken]]
