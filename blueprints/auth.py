from flask import request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from jwt import DecodeError

from db.model import User
from events.auth import TokenAuthEventHanlder
from events.factorys import event_handler_for
from utils.http import ValidationError, AuthError, ok_response, error_response

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


def authenticate_user(email: str, psswd: str):
    usr = User.query.filter_by(email=email).first()
    if usr and usr.password_is_valid(psswd):
        return usr


@auth_blueprint.route('/token-auth', methods=('POST',))
def authenticate():
    handler = event_handler_for(request)
    # return handler.get_response()

    email = request.json.get('email', None)
    psswd = request.json.get('password', None)
    if not email:
        raise ValidationError(field_name='email', messages=['Field is required'])
    if not psswd:
        raise ValidationError(field_name='psswd', messages=['Field is required'])
    user = authenticate_user(email, psswd)
    if not user: raise AuthError('Invalid credentials')
    return ok_response({'token': create_access_token(identity=user.as_dict())})


@auth_blueprint.route('/token-ping', methods=('GET',))
@jwt_required
def ping():
    return {
        'msg': 'pong!'
    }
