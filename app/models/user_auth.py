from datetime import datetime
from enum import Enum
from typing import List, Optional
from odmantic import Model, EmbeddedModel


class Service(str, Enum):
    DISCORD = "discord"


class AuthToken(EmbeddedModel):
    """Contains the information required to authenticate a user

    Attributes:
        service (Service): The service this authentication is for
        token (str): Token used to authenticate with
        info (Optional[str]): Optional information about the service and/or token
    """

    service: Service
    token: str
    info: Optional[str]


class User(Model):
    """Represents an authorized user

    Attributes:
        userid (int): Something Awful user id
        username (str): Something Awful user name
        reg_date (datetime): Date of registration on Something Awful
        perma_banned (Optional[datetime]): Flag to tell if the user was permabanned
        services (Optional[List[AuthToken]]): List of authed services
    """

    userid: int
    username: str
    reg_date: datetime
    perma_banned: Optional[datetime]
    services: Optional[List[AuthToken]]
