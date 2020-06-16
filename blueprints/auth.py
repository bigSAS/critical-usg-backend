from flask import request, Blueprint
from flask_jwt_extended import jwt_required, JWTManager
from jwt import DecodeError

from events.factorys import event_handler_for
from utils.http import AuthError, error_response

auth_blueprint = Blueprint('auth', __name__)
jwt = JWTManager()  # https://flask-jwt-extended.readthedocs.io/en/stable/api/


@auth_blueprint.errorhandler(Exception)
def handle_error(error: Exception):
    if isinstance(error, DecodeError):
        return handle_error(AuthError(f'Token decoding failed: {repr(error)}'))
    return error_response(error)


@jwt.expired_token_loader
def token_exipred(data: dict):
    raise AuthError(f'Token expired:\n{repr(data)}')


@jwt.invalid_token_loader
def token_invalid(message: str):
    raise AuthError(f'Token invalid: {message}')


@jwt.needs_fresh_token_loader
def token_not_fresh():
    raise AuthError(f'Fresh token required')


@jwt.revoked_token_loader
def token_not_fresh():
    raise AuthError(f'Not authorized')


@auth_blueprint.route('/token-auth', methods=('POST',))
def authenticate():
    """ Obtain JWT """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/register-user', methods=('POST',))
def register():
    """ Register new user (not admin) """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/token-ping', methods=('GET',))
@jwt_required
def ping():
    return {
        'msg': 'pong!'
    }
