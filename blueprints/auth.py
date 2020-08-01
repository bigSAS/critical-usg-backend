from flask import request, Blueprint
from flask_jwt_extended import JWTManager
from jwt import DecodeError

from events.factorys import event_handler_for
from utils.http import AuthError, error_response
from utils.permissions import restricted, superuser_only

auth_blueprint = Blueprint('auth', __name__)
jwt = JWTManager()  # https://flask-jwt-extended.readthedocs.io/en/stable/api/


# todo: zbadac errory dla invalid tokenow bo chyba cos nie do konca to dziala
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
    raise AuthError('Fresh token required')


@jwt.revoked_token_loader
def token_revoked():
    raise AuthError('Not authorized')


@auth_blueprint.route('/token-auth', methods=('POST',))
def authenticate():
    """ Obtain JWT """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/register-user', methods=('POST',))
def register_user():
    """ Register new user (not admin) """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/delete-user', methods=('POST',))
@restricted(['ADMIN'])
def delete_user():
    """ Register new user (not admin) """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/get-user-data', methods=('POST',))
@restricted(['ADMIN', 'USER'])
def get_user_data():
    """ Register new user (not admin) """
    return event_handler_for(request).get_response()


@auth_blueprint.route('/user-ping', methods=('GET', 'POST'))
@restricted(['USER'])
def user_ping():
    return {
        'msg': 'pong!'
    }


@auth_blueprint.route('/superuser-ping', methods=('GET', 'POST'))
@superuser_only
def superuser_ping():
    return {
        'msg': 'super!'
    }


@auth_blueprint.route('/open-ping', methods=('GET', 'POST'))
def open_ping():
    return {
        'msg': 'hello!'
    }
