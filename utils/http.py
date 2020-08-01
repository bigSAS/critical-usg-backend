import uuid
from typing import List, Union

from pydantic import BaseModel
from flask import Response, g

from config import Config
from db.models import ApiErrorModel, ResponseStatus, ResponseModel


class ApiError(Exception):
    def __init__(self, name: str, data: Union[List, str]):
        self.name = name
        self.data = data

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
    if data and not isinstance(data, dict) and not isinstance(data, BaseModel):
        raise ValueError('Data must be an istance of dict or pydantic.BaseModel')

    data_obj = data
    if isinstance(data, BaseModel):
        data_obj = data.dict()

    uid = g.get('uid', uuid.uuid4())
    return JsonResponse(
        status=200,
        response=ResponseModel(
            uid=uid,
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

    uid = g.get('uid', uuid.uuid4())
    return JsonResponse(
        status=http_status,
        response=ResponseModel(
            uid=uid,
            status=response_status,
            errors=[api_error.to_api_error_model()]
        ).json()
    )
