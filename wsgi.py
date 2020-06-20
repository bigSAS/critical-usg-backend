from flask import Flask, request
from flask_migrate import Migrate
from blueprints.auth import auth_blueprint, jwt
from db.model import db, bcrypt
from utils.http import ValidationError
from config import Config


class App(Flask): pass


def create_app():
    application = Flask(__name__, instance_relative_config=False)
    application.config.from_object(Config)
    db.init_app(application)
    mirgate = Migrate()
    mirgate.init_app(application, db)
    bcrypt.init_app(application)
    jwt.init_app(application)
    application.register_blueprint(auth_blueprint, url_prefix='/api')
    return application


app = create_app()


@app.before_request
def check_json_content_type():
    if request.method == "POST" and (request.content_type is None or 'application/json' not in request.content_type):
        raise ValidationError(['Content-Type - application/json only'])


@app.errorhandler
def handle_error(error: Exception):
    return handle_error(error)


if __name__ == '__main__':
    app.run(debug=Config.FLASK_DEBUG)
