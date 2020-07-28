from typing import Optional

from flask import Request
from flask_jwt_extended import create_access_token, get_jwt_identity
from pydantic.main import BaseModel

from db.models import TokenAuthEventRequestModel, TokenAuthEventResponseDataModel, UserEntityModel, \
    UserGroupEntityModel, RegisterUserEventRequestModel, RegisterUserEventResponseDataModel
from db.schema import User, GroupUser
from db.serializers import UserSerializer
from events.core import EventHandler, EventValidator
from events.validators import ObjectExist
from repository.base import ObjectNotFoundError
from repository.repos import UserRepository, UserGroupRepository
from utils.http import JsonResponse, AuthError, ok_response
from utils.managers import UserManager


class TokenAuthEventHandler(EventHandler):
    request_model_class = TokenAuthEventRequestModel

    def get_response(self) -> JsonResponse:
        user = self.__auth_user()
        if not user: raise AuthError('Invalid credentials')

        managed_user = UserManager(user=user)
        user_model = UserEntityModel.construct(
            id=user.id,
            username=user.username,
            email=user.email,
            is_superuser=user.is_superuser,
            is_deleted=user.is_deleted,
            groups=[UserGroupEntityModel.construct(id=g.id, name=g.name) for g in managed_user.get_groups()]
        )
        rdata_model = TokenAuthEventResponseDataModel.construct(
            token=create_access_token(identity=user_model.dict())
        )
        return ok_response(data=rdata_model, uid=self.request_uid)

    # noinspection PyBroadException
    def __auth_user(self) -> Optional[User]:
        try:
            user = UserRepository().get_by(
                email=self.request.json['email'].strip(),
                is_deleted=False
            )
            if user.password_is_valid(self.request.json['password'].strip()):
                return user
            return None
        except: return None


class RegisterUserEventHandler(EventHandler):
    request_model_class = RegisterUserEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: RegisterUserEventRequestModel = self.request_model
        user = User(
            email=rmodel.email,
            plaintext_password=rmodel.password,
            username=rmodel.username
        )
        UserRepository().save(user)
        self.__add_user_to_default_groups(user)

        managed_user = UserManager(user=user)
        rdata_model = RegisterUserEventResponseDataModel.construct(
            id=user.id,
            username=user.username,
            email=user.email,
            is_superuser=user.is_superuser,
            is_deleted=user.is_deleted,
            groups=[UserGroupEntityModel.construct(id=g.id, name=g.name) for g in managed_user.get_groups()]
        )
        return ok_response(data=rdata_model, uid=self.request_uid)

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


class GetUserDataRequestModel(BaseModel):
    user_id: Optional[int]
    # user_id: int  # -> debug


class GetUserDataEventHandler(EventHandler):
    request_model_class = GetUserDataRequestModel

    def get_response(self) -> JsonResponse:
        r = GetUserDataRequestModel(**self.request.json)
        user_id = r.user_id if r.user_id else get_jwt_identity()['id']
        managed_user = UserManager(user_id=user_id)
        user_model = UserEntityModel.construct(
            id=managed_user.user.id,
            username=managed_user.user.username,
            email=managed_user.user.email,
            is_superuser=managed_user.user.is_superuser,
            is_deleted=managed_user.user.is_deleted,
            groups=[UserGroupEntityModel.construct(id=g.id, name=g.name) for g in managed_user.get_groups()]
        )
        return ok_response(user_model.dict())
