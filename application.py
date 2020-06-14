from flask import Flask, request
from flask_migrate import Migrate
from blueprints.auth import auth_blueprint, jwt
from cfg import SECRET, DEBUG, DB_CONNETION_STRING

from db.model import db, bcrypt
from utils.http import error_response, ValidationError


class App(Flask): pass


def create_app():
    app = App(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNETION_STRING
    app.debug = DEBUG
    app.config['SECRET_KEY'] = SECRET
    db.init_app(app)
    mirgate = Migrate()
    mirgate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_blueprint, url_prefix='/api')
    return app


apk = create_app()


@apk.before_request
def check_json_content_type():
    if 'application/json' not in request.content_type:
        return error_response(ValidationError(['Content-Type - application/json only']))

if __name__ == '__main__':
    apk.run(debug=DEBUG)
