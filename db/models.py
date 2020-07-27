import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, UUID4, EmailStr, constr, validator


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


# @events
class TokenAuthEventRequestModel(BaseModel):
    uid: UUID4 = uuid.uuid4()
    email: EmailStr
    passwrod: constr(max_length=50)


class TokenAuthEventResponseModel(BaseModel):
    token: str


class RegisterUserEventRequestModel(BaseModel):
    email: EmailStr
    passwrod: constr(min_length=8, max_length=50)
    passwrod_repeat: constr(min_length=8, max_length=50)  # todo: add comare psswds validation l8r
    username: Optional[str]

    @validator('username')
    def username_max_len(cls, v: str):
        if len(v) > 50: raise ValueError('Max 50 chars')
        return v.strip()
