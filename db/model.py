from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
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

    def __repr__(self):
        return f'User'


class UserGroup(db.Model):
    """ User Group Entity """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)
    users = db.relationship('GroupUser', backref='group', lazy=True)

    def __repr__(self):
        return f'UserGroup()'


class GroupUser(db.Model):
    """ User in Group Entity """
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'GroupUser()'


class InstructionDocument(db.Model):
    """ Istruction Document Entity """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created = Column(DateTime)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated = Column(DateTime)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])

    def __init__(self, name: str, description: str, created_by: User):
        self.name = name
        self.description = description
        self.created_by_user_id = created_by.id
        self.created = datetime.utcnow()
        self.updated_by_user_id = None

    def __repr__(self):
        return f'IstructionDocument()'


class InstructionDocumentPage(db.Model):
    """ Istruction Document Page Entity """
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('instruction_document.id'), nullable=False)
    page_num = db.Column(db.Integer, default=0)
    json = db.Column(JSON, nullable=True)

    @hybrid_method
    def doc(self, document_id: int):
        return self.document_id == document_id

    def __repr__(self):
        return f'IstructionDocumentPage()'
