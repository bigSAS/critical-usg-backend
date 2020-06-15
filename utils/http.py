from enum import Enum
from typing import List
from flask import Response
from flask.json import dumps

from config import Config


class ApiError(Exception):
    def __init__(self, name: str, data):
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


class ValidationError(ApiError):
    def __init__(self, messages: List[str], field_name: str = 'NON_FIELD', ):
        if len(messages) == 0: raise ValueError('no messages passed in constructor')
        super().__init__(field_name, messages)


class ServerError(ApiError):
    def __init__(self, description):
        super().__init__('SERVER', description)


class AuthError(ApiError):
    def __init__(self, description: str = 'Invalid token'):
        super().__init__('AUTH', description)


class ResponseStatus(Enum):
    OK = 'OK'
    NOT_FOUND = 'NOT_FOUND'
    AUTH_ERROR = "AUTH_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVER_ERROR = 'SERVER_ERROR'


class ResponseBody:
    def __init__(self, status: ResponseStatus, api_error: ApiError = None, data: dict = None):
        self.status = status.value
        self.api_error = api_error
        self.data = data

    @property
    def body(self):
        return {
            'status': self.status,
            'errors': self.api_error.errros if self.api_error else [],
            'data': self.data
        }


class JsonResponse(Response):
    """ Json Response for api views """
    default_mimetype = 'application/json'
    default_status = 200

    def __init__(self, *args, **kwargs):
        json_obj = kwargs.pop('json', None)
        kwargs['response'] = dumps(json_obj) if json_obj else None
        super().__init__(*args, **kwargs)


ERROR_STATUS_MAP = {
    'NotFound': (404, ResponseStatus.NOT_FOUND),
    'AuthError': (401, ResponseStatus.AUTH_ERROR),
    'ValidationError': (400, ResponseStatus.VALIDATION_ERROR)
}


def ok_response(data: dict):
    return JsonResponse(
        status=200,
        json=ResponseBody(ResponseStatus.OK, data=data).body
    )


def error_response(error: Exception):
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
        json=ResponseBody(response_status, api_error).body
    )
