import logging
from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS
from blueprints.auth import auth_blueprint, jwt
from blueprints.instruction_document import instruction_document_blueprint
from db.schema import db, bcrypt
from utils.http import ValidationError, error_response
from config import Config

log_level = logging.DEBUG if Config.FLASK_DEBUG else logging.ERROR
print('LOG LEVEL', log_level)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.DEBUG,
    format='[%(asctime)s] | [%(levelname)s] | [%(name)s] | %(message)s'
)
logging.debug(f'Log level - {log_level}')


def create_app():
    application = Flask(__name__, instance_relative_config=False)
    allow_origins = ['*']  # todo: read from container config on prd
    CORS(application, origins=allow_origins)
    application.config.from_object(Config)
    db.init_app(application)
    mirgate = Migrate()
    mirgate.init_app(application, db)
    bcrypt.init_app(application)
    jwt.init_app(application)
    application.register_blueprint(auth_blueprint, url_prefix='/api')
    application.register_blueprint(instruction_document_blueprint, url_prefix='/api/instruction-documents')
    return application

app = create_app()


@app.before_request
def check_json_content_type():
    logging.debug(f'before req: {repr(request)}')
    if request.method == "POST" and (request.content_type is None or 'application/json' not in request.content_type):
        raise ValidationError('Content-Type - application/json only')


@app.errorhandler
def handle_error(error: Exception):
    return error_response(error)


if __name__ == '__main__':
    app.run(debug=Config.FLASK_DEBUG)
