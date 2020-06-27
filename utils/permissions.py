from functools import wraps
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity

from db.model import User
from managers.users import UserManager
from repository.repos import UserRepository, UserGroupRepository
from utils.http import ForbiddenError


def superuser_only(func):
    @wraps(func)
    @jwt_required
    def wrapper(*args, **kwargs):
        user_data: dict = get_jwt_identity()
        user: User = UserRepository().get(user_data['id'])
        if user.is_deleted: ForbiddenError('Account deleted')
        if not user.is_superuser: raise ForbiddenError('Admin only')
        return func(*args, **kwargs)
    return wrapper


def has_group_permission(user: User, groups: List[str]) -> bool:
    has_permission = False
    managed_user = UserManager(user)
    for g in groups:
        group = UserGroupRepository().get_by(name=g)
        if managed_user.belongs_to_group(group):
            has_permission = True
            break
    return has_permission


def restricted(groups: List[str]):
    if len(groups) == 0: raise ValueError('groups not specified!')

    def decorator(func):
        @wraps(func)
        @jwt_required
        def wrapper(*args, **kwargs):
            user_data: dict = get_jwt_identity()
            user: User = UserRepository().get(user_data['id'])
            if user.is_deleted: ForbiddenError('Account deleted')
            if not has_group_permission(user, groups) and not user.is_superuser:
                raise ForbiddenError(f'Only alowed for users in groups: {groups}')
            return func(*args, **kwargs)
        return wrapper
    return decorator
