from flask import Request
from flask_jwt_extended import create_access_token

from db.model import User, db
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, IsRequired, EmailCorrect, TheSame, MinLen
from utils.http import JsonResponse, AuthError, ok_response


class TokenAuthEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            MaxLen(field_name='email', max_len=200, value=request.json.get('email', None)),
            EmailCorrect(field_name='email', value=request.json.get('email', None)),
            IsRequired(field_name='password', value=request.json.get('password', None))
        ])


class TokenAuthEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, TokenAuthEventValidator(request))

    def get_response(self) -> JsonResponse:
        user = self.__auth_user()
        if not user: raise AuthError('Invalid credentials')
        identity = user.as_dict()
        identity['user_groups'] = ['foo', 'bar']  # todo: user groups model
        return ok_response({'token': create_access_token(identity=identity)})

    def __auth_user(self):
        usr = User.query.filter_by(email=self.request.json['email'].strip()).first()
        if usr and usr.password_is_valid(self.request.json['password'].strip()):
            return usr


class RegisterUserEventValidator(EventValidator):
    """
    todo: @validation
    * more password rules
    * username exclude special chars, only allow . and - (inside of username)
    """
    def __init__(self, request: Request):
        super().__init__([
            EmailCorrect(field_name='email', value=request.json.get('email', None)),
            MinLen(field_name='email', min_len=6, value=request.json.get('email', None)),
            MaxLen(field_name='email', max_len=200, value=request.json.get('email', None)),
            MinLen(field_name='password', min_len=8, value=request.json.get('password', None)),
            MaxLen(field_name='password', max_len=50, value=request.json.get('password', None)),
            TheSame(field_name='password_repeat', second_field_name='password',
                    value=request.json.get('password_repeat', None), second_value=request.json.get('password', None)),
            MaxLen(field_name='username', max_len=50, value=request.json.get('username', None), optional=True),
        ])


class RegisterUserEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, RegisterUserEventValidator(request))

    def get_response(self) -> JsonResponse:
        user = User(
            email=self.request.json['email'],
            plaintext_password=self.request.json['password'],
            username=self.request.json.get('username', None)
        )
        db.session.add(user)
        db.session.commit()
        return ok_response(user.as_dict())
