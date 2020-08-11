import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, UUID4, EmailStr, constr, validator, root_validator

from cusg.repository.helpers import must_exist_by_pk, must_exist_by
from cusg.repository.repos import UserRepository, InstructionDocumentRepository, InstructionDocumentPageRepository


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
    slug: str
    created: datetime
    created_by_user_id: int
    description: Optional[constr(min_length=1, max_length=500)] = None
    updated: Optional[datetime] = None
    updated_by_user_id: Optional[int] = None


class InstructionDocumentPageEntityModel(OrmModel):
    id: int
    document_id: int
    page_num: int
    md: str
    html: str


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
    def passwords_match(cls, v, values: dict):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class DeleteUserEventRequestModel(BaseEventRequestModel):
    user_id: int

    @classmethod
    @validator('user_id')
    def user_must_exist(cls, v: int):
        must_exist_by_pk(UserRepository(), v)
        return v


class GetUserDataEventRequestModel(BaseEventRequestModel):
    user_id: Optional[int]


class AddInstructionDocumentEventRequestModel(BaseEventRequestModel):
    name: constr(min_length=3, max_length=200)
    description: Optional[constr(min_length=1, max_length=500)]


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


class AddInstructionDocumentPageEventRequestModel(BaseEventRequestModel):
    document_id: int
    md: str

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


class UpdateInstructionDocumentPageEventRequestModel(BaseEventRequestModel):
    page_id: int
    md: str

    @classmethod
    @validator('document_id')
    def doc_must_exist(cls, v: int):
        must_exist_by_pk(InstructionDocumentRepository(), v)
        return v


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


class GetInstructionDocumentEventRequestModel(BaseEventRequestModel):
    # todo: pydantic validation not triggering ;( dunno why
    document_id: int = None
    document_slug: constr(min_length=2) = None

    @classmethod
    @root_validator(pre=True)
    def check_input(cls, values: dict):
        doc_slug = values.get('document_slug', None)
        doc_id = values.get('document_id', None)
        print('validation doc id', doc_id)
        print('validation doc slug', doc_slug)
        if doc_slug is None and doc_id is None:
            raise ValueError('document_slug or document_id is required')
        if doc_slug is not None and doc_id is not None:
            raise ValueError('provide only document_slug or only document_id')
        if doc_slug is not None:
            must_exist_by(InstructionDocumentRepository(), by='slug', value=doc_slug)
        if doc_id is not None:
            must_exist_by_pk(InstructionDocumentRepository(), doc_id)
        return values


class GetInstructionDocumentEventResponsedataModel(InstructionDocumentEntityModel):
    pages: List[InstructionDocumentPageEntityModel]
