import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, UUID4, EmailStr, constr


class OrmModel(BaseModel):
    class Config:
        orm_mode = True


# @base models
class ResponseStatus(str, Enum):
    OK = 'OK'
    NOT_FOUND = 'NOT_FOUND'
    AUTH_ERROR = "AUTH_ERROR"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVER_ERROR = 'SERVER_ERROR'


class ApiErrorModel(BaseModel):
    name: str
    message: str


class ResponseModel(BaseModel):
    status: ResponseStatus
    data: Optional[dict]
    errors: List[ApiErrorModel] = []
    uid: UUID4 = uuid.uuid4()


# @entities
class UserGroupEntityModel(OrmModel):
    id: int
    name: str


class UserEntityModel(OrmModel):
    id: int
    username: str
    email: EmailStr
    is_superuser: bool
    is_deleted: bool
    groups: List[UserGroupEntityModel]


# @event models
class TokenAuthEventRequestModel(BaseModel):
    uid: UUID4 = uuid.uuid4()
    email: EmailStr = constr(min_length=5, max_length=200)
    passwrod: str = constr(min_length=8, max_length=50)


class TokenAuthEventResponseModel(BaseModel):
    token: str


