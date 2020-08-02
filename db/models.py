import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, UUID4, EmailStr, constr, validator

from repository.helpers import must_exist_by_pk
from repository.repos import UserRepository, InstructionDocumentRepository, InstructionDocumentPageRepository


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
    uid: Optional[UUID4]
    status: ResponseStatus
    data: Optional[dict] = None
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


class InstructionDocumentEntityModel(OrmModel):
    id: int
    name: str
    created: datetime
    created_by_user_id: int
    description: Optional[constr(min_length=1, max_length=500)] = None
    updated: Optional[datetime] = None
    updated_by_user_id: Optional[int] = None


class InstructionDocumentPageEntityModel(OrmModel):
    id: int
    document_id: int
    page_num: int
    json_data: Optional[dict] = None


# @events
class BaseEventRequestModel(BaseModel):
    uid: UUID4 = uuid.uuid4()


class TokenAuthEventRequestModel(BaseEventRequestModel):
    email: EmailStr
    password: constr(min_length=1, max_length=50, strip_whitespace=True)


class TokenAuthEventResponseDataModel(BaseModel):
    token: str


class RegisterUserEventRequestModel(BaseEventRequestModel):
    email: EmailStr
    password: constr(min_length=8, max_length=50)  # todo: add regex check
    password_repeat: constr(min_length=8, max_length=50)  # todo: add regex check
    username: Optional[constr(max_length=50)]  # todo contsr regex

    @classmethod
    @validator('password_repeat')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class RegisterUserEventResponseDataModel(UserEntityModel): pass


class DeleteUserEventRequestModel(BaseEventRequestModel):
    user_id: int

    @classmethod
    @validator('user_id')
    def user_must_exist(cls, v: int):
        must_exist_by_pk(UserRepository(), v)
        return v


class DeleteUserEventResponseDataModel(UserEntityModel): pass


class GetUserDataEventRequestModel(BaseEventRequestModel):
    user_id: Optional[int]


class GetUserDataEventResponseDataModel(UserEntityModel): pass


class AddInstructionDocumentEventRequestModel(BaseEventRequestModel):
    name: constr(min_length=3, max_length=200)
    description: Optional[constr(min_length=1, max_length=500)]


class AddInstructionDocumentEventResponseDataModel(InstructionDocumentEntityModel): pass


class DeleteInstructionDocumentEventRequestModel(BaseEventRequestModel):
    document_id: int

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class UpdateInstructionDocumentEventRequestModel(AddInstructionDocumentEventRequestModel):
    document_id: int

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class UpdateInstructionDocumentEventResponseDataModel(InstructionDocumentEntityModel): pass


class AddInstructionDocumentPageEventRequestModel(BaseEventRequestModel):
    document_id: int
    json_data: Optional[dict] = None

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class AddInstructionDocumentPageEventResponseDataModel(InstructionDocumentPageEntityModel): pass


class UpdateInstructionDocumentPageEventRequestModel(BaseEventRequestModel):
    page_id: int
    json_data: Optional[dict] = None

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class UpdateInstructionDocumentPageEventResponseDataModel(InstructionDocumentPageEntityModel): pass


class DeleteInstructionDocumentPageEventRequestModel(BaseEventRequestModel):
    page_id: int

    @classmethod
    @validator('page_id')
    def page_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentPageRepository(), v)
        return v


class ListInstructionDocumentEventRequestModel(BaseEventRequestModel):
    page: int = 1
    limit: int = 100


class ListInstructionDocumentEventResponseDataModel(BaseModel):
    total: int
    page: int
    prev_num: Union[int, None]
    next_num: Union[int, None]
    results: List[InstructionDocumentEntityModel]


class SearchInstructionDocumentEventRequestModel(ListInstructionDocumentEventRequestModel):
    search: constr(min_length=3, max_length=100)


class SearchInstructionDocumentEventResponseDataModel(ListInstructionDocumentEventResponseDataModel): pass


class GetInstructionDocumentEventRequestModel(BaseEventRequestModel):
    document_id: int

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class GetInstructionDocumentEventResponsedataModel(InstructionDocumentEntityModel):
    pages: List[InstructionDocumentPageEntityModel]
