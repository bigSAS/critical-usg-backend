from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from cusg import db
from cusg.config import ENV, Config, TConfig


app = Flask(__name__)
dburi = TConfig.SQLALCHEMY_DATABASE_URI if ENV == 'test' else Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = dburi

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
