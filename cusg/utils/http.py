import uuid, logging
from json import dumps, loads
from typing import List, Union

from pydantic import BaseModel
from flask import Response, g, request

from cusg.config import ENV
from cusg.db.models import ApiErrorModel, ResponseStatus, ResponseModel


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
    def __init__(self, message: str, field_name: str = 'NON_FIELD'):
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

    return JsonResponse(
        status=200,
        response=ResponseModel(
            uid=g.get('uid', uuid.uuid4()),
            status=ResponseStatus.OK,
            data=data_obj
        ).json()
    )


def hide_passwords(data: dict):
    sensitive_keys = ['password', 'secret']
    for key in data.keys():
        if key.lower() in sensitive_keys or len([k for k in sensitive_keys if k in key.lower()]) > 0:
            data[key] = '*****'
    return data


def error_response(error: Exception = None):
    http_status, response_status = ERROR_STATUS_MAP.get(type(error).__name__, (500, ResponseStatus.SERVER_ERROR))
    if not isinstance(error, ApiError):
        if ENV == 'dev': raise error
        api_error = ApiError(name='SERVER', data=repr(error))
    else:
        api_error = error

    rm = ResponseModel(
        uid=g.get('uid', uuid.uuid4()),
        status=response_status,
        errors=[api_error.to_api_error_model()]
    )
    if response_status == ResponseStatus.SERVER_ERROR:
        req_data = hide_passwords(request.json)
        res_data = hide_passwords(loads(rm.json()))

        request_preety = dumps(req_data, indent=2, sort_keys=True)
        respons_preety = dumps(res_data, indent=2, sort_keys=True)
        logging.error(f'[SERVER_ERROR]\n'
                      f'request:\n{request_preety}\n'
                      f'response:\n{respons_preety}')
    else:
        logging.debug(f'response -> {rm}')
    return JsonResponse(
        status=http_status,
        response=rm.json()
    )
