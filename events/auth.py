from typing import List, Optional

from flask import Request
from flask_jwt_extended import create_access_token, get_jwt_identity
from pydantic.main import BaseModel
from pydantic.networks import EmailStr

from db.schema import User, GroupUser, OrmModel, UserGroup
from db.serializers import UserSerializer
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, IsRequired, EmailCorrect, TheSame, MinLen, ObjectExist
from repository.base import ObjectNotFoundError
from repository.repos import UserRepository, UserGroupRepository, GroupUserRepository
from utils.http import JsonResponse, AuthError, ok_response
from utils.managers import UserManager


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
        identity = UserSerializer(user).data
        return ok_response({'token': create_access_token(identity=identity)})

    # noinspection PyBroadException
    def __auth_user(self):
        try:
            user = UserRepository().get_by(
                email=self.request.json['email'].strip(),
                is_deleted=False
            )
            if user.password_is_valid(self.request.json['password'].strip()):
                return user
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
        user = User(
            email=self.request.json['email'],
            plaintext_password=self.request.json['password'],
            username=self.request.json.get('username', None)
        )
        UserRepository().save(user)
        self.__add_user_to_default_groups(user)
        data = UserSerializer(user).data
        return ok_response(data)

    @staticmethod
    def __add_user_to_default_groups(user: User):
        user_groups = ('USER',)
        for group_name in user_groups:
            try:
                repo = UserGroupRepository()
                user_group = repo.get_by(name=group_name)
                group_user = GroupUser(group_id=user_group.id, user_id=user.id)
                repo.save(group_user)
            except ObjectNotFoundError as e:
                raise ValueError(f'{group_name} user group not exists, check db defaults.\n{repr(e)}')


class DeleteUserEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            ObjectExist(UserRepository, request.json.get('user_id', None), 'user_id')
        ])


class DeleteUserEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, DeleteUserEventValidator(request))

    def get_response(self) -> JsonResponse:
        managed_user = UserManager(user_id=self.request.json['user_id'])
        managed_user.delete()
        serializer = UserSerializer(managed_user.user)
        return ok_response(serializer.data)


class UserGroupModel(OrmModel):
    id: int
    name: str


class GetUserModel(OrmModel):
    id: int
    username: str
    email: EmailStr
    is_superuser: bool
    is_deleted: bool
    groups: List[UserGroupModel]


class GetUserDataRequestModel(BaseModel):
    user_id: Optional[int]
    # user_id: int  # -> debug


class GetUserDataEventHandler(EventHandler):
    request_model_class = GetUserDataRequestModel

    def get_response(self) -> JsonResponse:
        r = GetUserDataRequestModel(**self.request.json)
        user_id = r.user_id if r.user_id else get_jwt_identity()['id']
        user = UserRepository().get(user_id)
        user_groups = GroupUserRepository().filter(GroupUser.user_id == user.id)
        group_ids = list(set([ug.group_id for ug in user_groups]))
        groups = UserGroupRepository().filter(UserGroup.id.in_(group_ids))
        user_model = GetUserModel.construct(
            id=user.id,
            username=user.username,
            email=user.email,
            is_superuser=user.is_superuser,
            is_deleted=user.is_deleted,
            groups=[UserGroupModel.construct(id=g.id, name=g.name) for g in groups]
        )
        return ok_response(user_model.dict())
