from datetime import datetime
from json import loads

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.types import JSON

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
    is_deleted = db.Column(db.Boolean, default=False)

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

    def delete(self):
        self.is_deleted = True

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_superuser': self.is_superuser,
            'groups': [ug.name for ug in self.user_groups],
            'is_deleted': self.is_deleted
        }

    def __str__(self):
        return f'User{self.as_dict()}'

    def __repr__(self):
        return self.__str__()


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


class InstructionDocument(db.Model):
    """ Istruction Document Entity """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created = Column(DateTime)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated = Column(DateTime)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, name: str, description: str, created_by: User):
        self.name = name
        self.description = description
        self.created_by_user_id = created_by.id
        self.created = datetime.utcnow()

    def update_doc(self, updated_by: User, **kwargs):
        valid_kwargs = ('name', 'description')
        self.updated_by_user_id = updated_by.id
        for k, v in kwargs.items():
            if k in valid_kwargs: setattr(self, k, v)
        self.updated = datetime.utcnow()

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created': str(self.created),
            'created_by_user_id': self.created_by_user_id,
            'updated': str(self.updated),
            'updated_by_user_id': self.created_by_user_id,
        }

    def __repr__(self):
        return f'IstructionDocument({self.as_dict()})'


class InstructionDocumentPage(db.Model):
    """ Istruction Document Page Entity """
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('instruction_document.id'), nullable=False)
    page_num = db.Column(db.Integer, default=0)
    json = db.Column(JSON, nullable=True)

    # @property
    # def data(self):
    #     return loads(self.json_data) if self.json_data else None

    def as_dict(self):
        return {
            'id': self.id,
            'document_id': str(self.document_id),
            'page_num': self.page_num,
            'json': self.json,
            # 'json_data': self.json_data,  # todo: uncomment for debug
            # 'data': self.data
        }

    def __repr__(self):
        return f'IstructionDocumentPage({self.as_dict()})'
