import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, UUID4


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
