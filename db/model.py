from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    """ User Entity """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    _password = db.Column(db.LargeBinary(100))
    is_superuser = db.Column(db.Boolean, default=False)
    groups = db.relationship('GroupUser', backref='user', lazy=True)

    def __init__(self, email: str,  plaintext_password: str, username: str = None, is_superuser: bool = False):
        self.email = email
        self.password = plaintext_password
        self.username = username
        self.is_superuser = is_superuser

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext_password: str):
        self._password = bcrypt.generate_password_hash(plaintext_password)

    @hybrid_method
    def password_is_valid(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @property
    def user_groups(self):
        group_ids = set([gu.group_id for gu in self.groups])
        return UserGroup.query.filter(UserGroup.id.in_(group_ids)).all()

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_superuser': self.is_superuser,
            'groups': [ug.name for ug in self.user_groups]
        }

    def __repr__(self):
        return f'User{self.as_dict()}'


class UserGroup(db.Model):
    """ User Group Entity """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)
    users = db.relationship('GroupUser', backref='group', lazy=True)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f'UserGroup({self.as_dict()})'


class GroupUser(db.Model):
    """ User in Group Entity """
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'GroupUser({self.as_dict()})'
