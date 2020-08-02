from flask import Request, g

from db.models import BaseEventRequestModel
from utils.http import JsonResponse, ValidationError
from abc import ABC
from pydantic import ValidationError as VError


class EventHandler(ABC):
    request_model_class = None
    """ Base event handler class """
    def __init__(self, request: Request):
        setattr(g, 'uid', request.json.get('uid', None))
        print('@G -> request uid:', g.get('uid', None))
        self.__request = request
        self.__request_model = self.__get_request_model(request)

    @property
    def request(self):
        return self.__request

    @property
    def request_model(self):
        return self.__request_model

    def get_response(self) -> JsonResponse:
        raise NotImplementedError('Implement in child class')

    def __get_request_model(self, request) -> BaseEventRequestModel:
        if not self.request_model_class: raise NotImplementedError('request_model_class not set')
        else:
            try:
                return self.request_model_class(**request.json)
            except VError as e:
                field_name, message = extract_error(e)
                raise ValidationError(
                    field_name=field_name,
                    message=message,
                )


def extract_error(error: VError):
    first_error = error.errors()[0]
    return first_error['loc'][0], first_error['msg']
