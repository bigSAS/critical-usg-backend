from typing import Any, List
from flask import Request, g

from db.models import BaseEventRequestModel
from utils.http import JsonResponse, ValidationError
from abc import ABC
from pydantic import ValidationError as VError


class Validator(ABC):
    """
    Parent Validator class
    @:param value - value to be validated
    @:param field_name - field name if validation is related to model
    @:param optional - set True when field is optional (not required, and validated only when has value)
    """
    def __init__(self, value: Any, field_name: str = "NON_FIELD", optional: bool = False):
        self.value = value
        self.field_name = field_name
        self.optional = optional
        self.__validate_required()

    def has_value(self):
        return self.value is not None

    def cleaned_value(self):
        return self.value.strip() if isinstance(self.value, str) else self.value

    def validate(self):
        """ must raise ValidationError when validation fails """
        raise NotImplementedError('Implement in child class')

    def __validate_required(self):
        if not self.optional and (not self.has_value() or self.cleaned_value() == ''):
            raise ValidationError('Field is required', self.field_name)


class EventValidator(ABC):
    def __init__(self, validators: List[Validator] = tuple()):
        self.__validators = validators

    @property
    def validators(self):
        return self.__validators

    def validate(self):
        for validator in self.validators:
            validator.validate()


class EventHandler(ABC):
    request_model_class = None
    """ Base event handler class """
    def __init__(self, request: Request, event_validator: EventValidator = None, validate: bool = True):
        setattr(g, 'uid', request.json.get('uid', None))
        print('@G -> request uid:', g.get('uid', None))
        self.__request = request
        self.__request_model = self.__get_request_model(request)

        self.__event_validator = event_validator  # todo: rm when refactor done
        if validate: self.validate()  # todo: rm when refactor done

    @property
    def request(self):
        return self.__request

    @property
    def request_model(self):
        return self.__request_model

    def validate(self):
        if self.__event_validator:
            self.__event_validator.validate()

    def get_response(self) -> JsonResponse:
        raise NotImplementedError('Implement in child class')

    def __get_request_model(self, request) -> BaseEventRequestModel:
        if not self.request_model_class:
            print('request_model_class not set')
        # todo: enable ??? <- refactor done ? after review
        # todo: enable when refactor done
        # if not self.request_model_class: raise NotImplementedError('request_model_class not set')
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
