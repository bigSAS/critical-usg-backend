from typing import Any, List
from flask import Request
from utils.http import JsonResponse


class Validator:
    def __init__(self, value: Any, field_name: str = "NON_FIELD"):
        self.value = value
        self.field_name = field_name

    def validate(self):
        """ must raise ValidationError when validation fails """
        raise NotImplementedError('Implement in child class')


class EventValidator:
    def __init__(self, validators: List[Validator] = tuple()):
        self.__validators = validators

    @property
    def validators(self):
        return self.__validators

    def validate(self):
        for validator in self.validators:
            validator.validate()


class EventHandler:
    """ Base event handler class """
    def __init__(self, request: Request, event_validator: EventValidator = None):
        self.__request = request
        self.__event_validator = event_validator
        self.validate()

    @property
    def request(self):
        return self.__request

    @property
    def event_validator(self):
        return self.__event_validator

    def validate(self):
        if self.__event_validator:
            self.__event_validator.validate()

    def get_response(self) -> JsonResponse:
        raise NotImplementedError('Implement in child class')
