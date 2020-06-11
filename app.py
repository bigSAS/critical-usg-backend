from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from utils.auth import authenticate_user


class App(Flask): pass


app = App(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'  # todo: strong secret
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)  # todo: parametrize jwt lifetime, add refresh token ???
migrate = Migrate(app, db)


@app.route('/', methods=('POST',))
def hello_world():
    """ Hello world - flask app"""
    return {
        "hello": "world - app is live and running :)"
    }


@app.route('/token-auth', methods=('POST',))
def authenticate():
    """ get jwt token """
    # todo: midleware to allow only valid application/json requests

    email = request.json.get("email", None)
    psswd = request.json.get("password", None)

    if not email or not psswd: return jsonify({"msg": "email and password are required"}), 400
    user = authenticate_user(email, psswd)
    if not user: return jsonify({"msg": "invalid credentials"}), 401

    access_token = create_access_token(identity=user.as_dict())
    return jsonify(access_token=access_token), 200


@app.route('/get-user-data', methods=['GET'])
@jwt_required
def get_user_data_from_jwt():
    # todo: delete later
    return jsonify(get_jwt_identity()), 200


if __name__ == '__main__':
    app.run(debug=True)

# noinspection PyUnresolvedReferences
from db import model
