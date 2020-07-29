import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, UUID4, EmailStr, constr, validator

from repository.repos import UserRepository


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
    uid: Optional[UUID4]  # todo: mandatory when refactor done
    status: ResponseStatus
    data: Optional[dict]
    errors: List[ApiErrorModel] = []


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
class BaseEventRequest(BaseModel):
    uid: UUID4 = uuid.uuid4()


class TokenAuthEventRequestModel(BaseEventRequest):
    email: EmailStr
    password: constr(min_length=1, max_length=50, strip_whitespace=True)


class TokenAuthEventResponseDataModel(BaseModel):
    token: str


class RegisterUserEventRequestModel(BaseEventRequest):
    email: EmailStr
    password: constr(min_length=8, max_length=50)  # todo: add regex check
    password_repeat: constr(min_length=8, max_length=50)  # todo: add regex check
    username: Optional[str]  # todo contr regex

    @validator('username')
    def username_max_len(cls, v: str):
        if v and len(v) > 50: raise ValueError('Max 50 chars')
        return v

    @validator('password_repeat')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class RegisterUserEventResponseDataModel(UserEntityModel): pass


class DeleteUserEventRequestModel(BaseEventRequest):
    user_id: int

    @validator('user_id')
    def user_must_exist(cls, v: int):
        usr = UserRepository().get(entity_id=v, ignore_not_found=True)
        if not usr: raise ValueError(f'User[{v}] not exists')


class DeleteUserEventResponseDataModel(UserEntityModel): pass
