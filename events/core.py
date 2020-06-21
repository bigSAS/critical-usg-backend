from typing import Any, List
from flask import Request
from utils.http import JsonResponse, ValidationError
from abc import ABC


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
            raise ValidationError(['Field is required'], self.field_name)


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
    """ Base event handler class """
    def __init__(self, request: Request, event_validator: EventValidator = None, validate: bool = True):
        self.__request = request
        self.__event_validator = event_validator
        if validate: self.validate()

    @property
    def request(self):
        return self.__request

    def validate(self):
        if self.__event_validator:
            self.__event_validator.validate()

    def get_response(self) -> JsonResponse:
        raise NotImplementedError('Implement in child class')
