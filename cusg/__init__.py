import logging, os

from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_cors import CORS

from cusg.blueprints.auth import auth_blueprint, jwt
from cusg.blueprints.instruction_document import instruction_document_blueprint

from cusg.config import Config, ENV
from cusg.db.schema import db, bcrypt, UserGroup
from cusg.repository.repos import UserGroupRepository
from cusg.utils.http import ValidationError, error_response


def create_app(test_config=None):
    print('ENV:', ENV)
    application = Flask(__name__, instance_relative_config=False)
    allowed_hosts = os.environ.get('CUSG_ALLOWED_HOSTS', '*')
    if allowed_hosts == '*': logging.warning('CUSG_ALLOWED_HOSTS not set')
    CORS(application, resources={r"/api/*": {"origins": allowed_hosts.split(' ')}})
    conf = test_config if test_config else Config
    if ENV != 'test':
        log_level = logging.DEBUG if Config.FLASK_DEBUG else logging.WARNING
        print('LOG LEVEL:', "DEBUG" if log_level == logging.DEBUG else "WARNING")
        print('CUSG ENV:', ENV)
        logging.basicConfig(
            filename='cusg/logs/app.log',
            level=logging.DEBUG,
            format='[%(asctime)s] | [%(levelname)s] | [%(name)s] | %(message)s'
        )
        logging.debug(f'Log level - {log_level}')
        logging.info(f'allowed_hosts: {allowed_hosts}')
        logging.getLogger('flask_cors').level = logging.DEBUG
    application.config.from_object(conf)
    db.init_app(application)
    mirgate = Migrate()
    mirgate.init_app(application, db)
    bcrypt.init_app(application)
    jwt.init_app(application)
    application.register_blueprint(auth_blueprint, url_prefix='/api')
    application.register_blueprint(instruction_document_blueprint, url_prefix='/api/instruction-documents')
    application.before_request(check_json_content_type)
    application.errorhandler(handle_error)
    create_default_groups(application)

    @application.route('/doc-admin', methods=('GET',))
    def doc_admin(): return render_template('doc-admin.html')
    return application


def check_json_content_type():
    logging.debug(f'before req: {repr(request)}')
    if request.method == "POST" and (request.content_type is None or 'application/json' not in request.content_type):
        raise ValidationError('Content-Type - application/json only')


def handle_error(error: Exception):
    return error_response(error)


DEFAULT_USER_GROUPS = ('USER', 'ADMIN')


def create_default_groups(app):
    with app.app_context():
        print('Create default user groups')
        created_groups = []
        for user_group in DEFAULT_USER_GROUPS:
            existing_ug = UserGroupRepository().get_by(name=user_group, ignore_not_found=True)
            if not existing_ug:
                user_group = UserGroup(name=user_group)
                UserGroupRepository().save(user_group)
                created_groups.append(user_group)
        db.session.commit()
        if len(created_groups) > 0:
            print(f'Created {len(created_groups)}:', created_groups)
        else:
            print('No new user groups created...')
