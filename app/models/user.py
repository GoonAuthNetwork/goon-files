from datetime import datetime
from typing import List, Optional
from odmantic import Model
import pydantic

from .authtoken import AuthToken


class User(Model):
    """Represents an authorized user

    Attributes:
        userid (int): Something Awful user id
        username (str): Something Awful user name
        reg_date (datetime): Date of registration on Something Awful
        perma_banned (Optional[datetime]): Flag to tell if the user was permabanned
        services (Optional[List[AuthToken]]): List of authed services
    """

    userId: int
    userName: str
    regDate: datetime
    permaBanned: Optional[datetime]
    services: Optional[List[AuthToken]]
    createdAt: datetime


class NewUser(pydantic.BaseModel):
    userId: int = pydantic.Field(..., title="SA User Id", gt=0)
    userName: str = pydantic.Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    regDate: datetime
    services: Optional[List[AuthToken]]
