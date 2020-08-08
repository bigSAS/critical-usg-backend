from typing import Optional

from flask_jwt_extended import create_access_token, get_jwt_identity

from cusg.db.models import TokenAuthEventRequestModel, TokenAuthEventResponseDataModel, \
    RegisterUserEventRequestModel, DeleteUserEventRequestModel, GetUserDataEventRequestModel
from cusg.db.schema import User, GroupUser
from cusg.events.core import EventHandler
from cusg.repository.base import ObjectNotFoundError
from cusg.repository.repos import UserRepository, UserGroupRepository
from cusg.utils.http import JsonResponse, AuthError, ok_response
from cusg.utils.managers import UserManager


class TokenAuthEventHandler(EventHandler):
    request_model_class = TokenAuthEventRequestModel

    def get_response(self) -> JsonResponse:
        user = self.__auth_user()
        if not user: raise AuthError('Invalid credentials')

        rdata_model = TokenAuthEventResponseDataModel.construct(
            token=create_access_token(identity=UserManager(user=user).user_model.dict())
        )
        return ok_response(data=rdata_model)

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
        return ok_response(data=UserManager(user=user).user_model)

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


class DeleteUserEventHandler(EventHandler):
    request_model_class = DeleteUserEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: DeleteUserEventRequestModel = self.request_model
        managed_user = UserManager(user_id=rmodel.user_id)
        managed_user.delete()
        return ok_response(data=managed_user.user_model)


class GetUserDataEventHandler(EventHandler):
    request_model_class = GetUserDataEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: GetUserDataEventRequestModel = self.request_model
        user_id = rmodel.user_id if rmodel.user_id else get_jwt_identity()['id']
        return ok_response(data=UserManager(user_id=user_id).user_model)
