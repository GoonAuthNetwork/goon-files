from datetime import datetime
from typing import List, Optional
from odmantic import Model

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
