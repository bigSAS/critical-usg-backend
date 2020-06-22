from functools import wraps
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity

from db.model import get_object, User
from utils.http import ForbiddenError


def superuser_only(func):
    @wraps(func)
    @jwt_required
    def wrapper(*args, **kwargs):
        user_data: dict = get_jwt_identity()
        user = get_object(User, id=user_data['id'])
        if not user.is_superuser:
            raise ForbiddenError('Admin only')
        return func(*args, **kwargs)
    return wrapper


def restricted(groups: List[str]):
    if len(groups) == 0: raise ValueError('groups not specified!')

    def decorator(func):
        @wraps(func)
        @jwt_required
        def wrapper(*args, **kwargs):
            user_groups = get_jwt_identity().get('user_groups', [])
            # todo: user groups from db?
            #  checking groups from jwt requires re-authenticate to refresh (maybe token refresh endpoint)
            #  checking permissions from db requires db call every request is made (performance related ???)
            has_permission = False
            for group in user_groups:
                if group in groups:
                    has_permission = True
                    break
            if not has_permission:
                raise ForbiddenError(f'Only alowed for users in groups: {groups}')
            return func(*args, **kwargs)
        return wrapper
    return decorator
