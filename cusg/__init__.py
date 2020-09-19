import logging

from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS

from cusg.blueprints.auth import auth_blueprint, jwt
from cusg.blueprints.files import files_blueprint
from cusg.blueprints.instruction_document import instruction_document_blueprint

from cusg.config import Config, ENV
from cusg.db.schema import db, bcrypt, UserGroup
from cusg.repository.repos import UserGroupRepository
from cusg.utils.http import ValidationError, error_response


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]\t[%(levelname)s]\t[%(name)s]\t%(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    # todo: setup app.logger
    logger.info(f'ENV: {ENV}')
    app = Flask(__name__, instance_relative_config=False)
    CORS(app, resources=r'/api/*')
    logging.getLogger('flask_cors').level = logging.DEBUG
    
    conf = test_config if test_config else Config
    app.config.from_object(conf)
    db.init_app(app)
    mirgate = Migrate()
    mirgate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_blueprint, url_prefix='/api')
    app.register_blueprint(instruction_document_blueprint, url_prefix='/api/instruction-documents')
    app.register_blueprint(files_blueprint, url_prefix='/api/files')
    app.register_error_handler(Exception, error_response)  # todo: err hanlding in error_response -> blueprint register default error_response
    app.before_request(check_json_content_type)
    
    with app.app_context():
        create_default_groups()
    
    return app

def check_json_content_type():
    logger.debug(f'before req: {repr(request)}')
    if request.path == '/api/files/add': return
    if request.method == "POST" and (request.content_type is None or 'application/json' not in request.content_type):
        raise ValidationError('Content-Type - application/json only')


DEFAULT_USER_GROUPS = ('USER', 'ADMIN')


def create_default_groups():
    logger.info('Create default user groups')
    created_groups = []
    for user_group in DEFAULT_USER_GROUPS:
        existing_ug = UserGroupRepository().get_by(name=user_group, ignore_not_found=True)
        if not existing_ug:
            user_group = UserGroup(name=user_group)
            UserGroupRepository().save(user_group)
            created_groups.append(user_group)
    db.session.commit()
    if len(created_groups) > 0:
        logger.info(f'Created {len(created_groups)}:')
    else:
        logger.info('No new user groups created...')
