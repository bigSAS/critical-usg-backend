from functools import wraps
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity

from cusg.db.schema import User
from cusg.utils.http import ForbiddenError
from cusg.utils.managers import UserManager
from cusg.repository.repos import UserRepository, UserGroupRepository


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


def has_group_permission(managed_user: UserManager, groups: List[str]) -> bool:
    has_permission = False
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
            managed_user = UserManager(user_id=user_data['id'])
            if managed_user.user.is_deleted: ForbiddenError('Account deleted')
            if not has_group_permission(managed_user, groups) and not managed_user.user.is_superuser:
                raise ForbiddenError(f'Only alowed for users in groups: {groups}')
            return func(*args, **kwargs)
        return wrapper
    return decorator
