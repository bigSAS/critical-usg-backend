from events.core import Validator
from repository.base import ObjectNotFoundError
from utils.http import ValidationError


class IsRequired(Validator):
    """ No other limitations except required """
    def __init__(self, value: str, field_name: str = "NON_FIELD"):
        super().__init__(value, field_name)

    def validate(self):
        pass


class TheSame(Validator):
    """ Values are the same (values cannot be None) """
    def __init__(self, value: str, second_value: str, field_name: str, second_field_name: str):
        super().__init__(value, field_name)
        self.second_value = second_value
        self.second_field_name = second_field_name

    def validate(self):
        if self.cleaned_value() != self.second_value.strip():
            raise ValidationError([f'Value must be the same as {self.second_field_name}'], self.field_name)


class MinLen(Validator):
    """ Minimum length """
    def __init__(self, value: str, min_len: int, field_name: str = "NON_FIELD", optional: bool = False):
        super().__init__(value, field_name, optional)
        self.min_len = min_len

    def validate(self):
        if self.has_value() and len(self.cleaned_value()) < self.min_len:
            raise ValidationError([f'Minimum length is {self.min_len}'], self.field_name)


class MaxLen(Validator):
    """ Maximum length """
    def __init__(self, value: str, max_len: int, field_name: str = "NON_FIELD", optional: bool = False):
        super().__init__(value, field_name, optional)
        self.max_len = max_len

    def validate(self):
        if self.has_value() and len(self.cleaned_value()) > self.max_len:
            raise ValidationError([f'Maximum length is {self.max_len}'], self.field_name)


class EmailCorrect(Validator):
    """ Valid email address """
    def __init__(self, value: str, field_name: str = "NON_FIELD", optional: bool = False):
        super().__init__(value, field_name, optional)

    def validate(self):  # todo: validate email via regex
        if self.has_value() and '@' not in self.cleaned_value():
            raise ValidationError([f'Email address is invalid'], self.field_name)


class ObjectExist(Validator):
    """ Model object exists """
    def __init__(self, repository_class, object_id: int, field_name: str = "NON_FIELD"):
        super().__init__(object_id, field_name)
        self.__repository_class = repository_class

    def validate(self):
        try:
            self.__repository_class().get(self.value)
        except ObjectNotFoundError as e:
            raise ValidationError([repr(e)], self.field_name)
