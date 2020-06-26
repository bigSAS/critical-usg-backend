from typing import List

from flask import Request
from flask_jwt_extended import create_access_token

from db.model import db, User, UserGroup, GroupUser
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, IsRequired, EmailCorrect, TheSame, MinLen, ObjectExist
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
        return ok_response({'token': create_access_token(identity=identity)})

    # noinspection PyBroadException
    def __auth_user(self):
        try:
            # todo: ! user from repo
            # user = get_object(User, email=self.request.json['email'].strip(), is_deleted=False)
            # if user.password_is_valid(self.request.json['password'].strip()):
            #     return user
            return None
        except: return None


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
    def __init__(self, request: Request, validate: bool = True):
        super().__init__(request, RegisterUserEventValidator(request), validate=validate)  # todo: rm validate ???

    def get_response(self) -> JsonResponse:
        user = self.__create_new_user()
        db.session.add(user)
        db.session.commit()
        user_groups = self.__add_user_default_groups(user)
        for ug in user_groups: db.session.add(ug)
        db.session.commit()
        return ok_response(user.as_dict())

    def __create_new_user(self) -> User:
        return User(
            email=self.request.json['email'],
            plaintext_password=self.request.json['password'],
            username=self.request.json.get('username', None)
        )

    @staticmethod
    def __add_user_default_groups(user: User) -> List[GroupUser]:
        user_groups = ('USER',)
        created_group_users = []
        # todo: ! use repo
        # for group in user_groups:
        #     try:
        #         user_group = get_object(UserGroup, name=group)
        #         created_group_users.append(GroupUser(group_id=user_group.id, user_id=user.id))
        #     except ObjectNotFoundError as e:
        #         raise ValueError(f'{group} user group not exists, check db defaults.\n{repr(e)}')
        return created_group_users


class DeleteUserEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            ObjectExist(User, request.json.get('user_id', None), 'user_id')
        ])


class DeleteUserEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, DeleteUserEventValidator(request))

    def get_response(self) -> JsonResponse:
        # todo: ! use repo
        return None
        # user = get_object(User, id=self.request.json['user_id'])
        # user.delete()
        # db.session.commit()
        # return ok_response(user.as_dict())
