from flask import Flask, request
from flask_migrate import Migrate
from blueprints.auth import auth_blueprint, jwt
from cfg import SECRET, DEBUG

from db.model import db, bcrypt
from utils.http import error_response, ValidationError


class App(Flask): pass


app = App(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.debug = True
app.config['SECRET_KEY'] = SECRET
app.register_blueprint(auth_blueprint, url_prefix='/api')


@app.before_request
def check_json_content_type():
    if 'application/json' not in request.content_type:
        return error_response(ValidationError(['Content-Type - application/json only']))

if __name__ == '__main__':
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    app.run(debug=DEBUG)
