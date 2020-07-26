import uuid
from enum import Enum
from typing import List, Union, Optional

from pydantic import BaseModel, UUID4

from flask import Response

from config import Config


class ApiError(Exception):
    # todo: refactor list of errors ? or first err 4eva ?
    def __init__(self, name: str, data: Union[List, str]):
        self.name = name
        self.data = data

    @property
    def errros(self) -> List[dict]:
        if isinstance(self.data, list):
            return [
                {
                    'name': self.name,
                    'message': message
                } for message in self.data
            ]
        return [{
            'name': self.name,
            'message': self.data
        }]

    def to_api_error_model(self):
        return ApiErrorModel(
            name=self.name,
            message=self.data
        )


class ValidationError(ApiError):
    def __init__(self, message: str, field_name: str = 'NON_FIELD', ):
        super().__init__(field_name, message)


class ServerError(ApiError):
    def __init__(self, description):
        super().__init__('SERVER', description)


class AuthError(ApiError):
    def __init__(self, description: str = 'Invalid token'):
        super().__init__('AUTH', description)


class ForbiddenError(ApiError):
    def __init__(self, description: str = 'Forbidden'):
        super().__init__('PERMISSION', description)


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

# todo: rm ???
# class ResponseBody:  # todo: pydantic with generic data [T]
#     def __init__(self, status: ResponseStatus, api_error: ApiError = None, data: dict = None,
#                  data_model: OrmModel = None):  # todo: data always from PydanticModel().dict() -> typi
#         # todo: validate -> only data or data_model can be passed ! ! !
#         self.status = status.value
#         self.api_error = api_error
#         self.data = data
#
#     @property
#     def body(self):  # todo: return ResponseBodyModel(self.status, self.api_error, self.data).data()
#         return {
#             'status': self.status,
#             'errors': self.api_error.errros if self.api_error else [],
#             'data': self.data
#         }


class JsonResponse(Response):
    """ Json Response for api views """
    default_mimetype = 'application/json'
    default_status = 200


ERROR_STATUS_MAP = {
    'NotFound': (404, ResponseStatus.NOT_FOUND),
    'AuthError': (401, ResponseStatus.AUTH_ERROR),
    'ValidationError': (400, ResponseStatus.VALIDATION_ERROR),
    'ForbiddenError': (403, ResponseStatus.FORBIDDEN)
}


def ok_response(data: Union[dict, BaseModel] = None):
    if isinstance(data, dict):
        data_obj = data
    elif isinstance(data, BaseModel):
        data_obj = data.dict()
    else:
        raise ValueError('Data must be an istance of dict or pydantic.BaseModel')
    return JsonResponse(
        status=200,
        response=ResponseModel(
            status=ResponseStatus.OK,
            data=data_obj
        ).json()
    )


def error_response(error: Exception = None):
    """ error handler for App """
    print("ERROR:")
    print(repr(error))
    http_status, response_status = ERROR_STATUS_MAP.get(type(error).__name__, (500, ResponseStatus.SERVER_ERROR))
    if not isinstance(error, ApiError):
        if Config.FLASK_DEBUG: raise error
        api_error = ApiError(name='SERVER', data=repr(error))
    else:
        api_error = error
    return JsonResponse(
        status=http_status,
        response=ResponseModel(
            status=ResponseStatus.OK,
            errors=[error.to_api_error_model()]
        ).json()
    )
