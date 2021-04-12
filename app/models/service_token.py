from enum import Enum
from typing import Optional
from odmantic import EmbeddedModel
import pydantic


class Service(str, Enum):
    DISCORD = "discord"
    OTHER = "other"


class ServiceToken(EmbeddedModel):
    """Contains the information required to authenticate a user

    Attributes:
        service (Service): The service this authentication is for
        token (str): Token used to authenticate with
        info (Optional[str]): Optional information about the service and/or token
    """

    service: Service
    token: str
    info: Optional[str]


class NewServiceToken(pydantic.BaseModel):
    service: Service
    token: str
    info: Optional[str]
