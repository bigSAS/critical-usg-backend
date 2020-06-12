from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app import db, bcrypt


class User(db.Model):
    """ User Entity """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    _password = db.Column(db.Binary(100))
    is_superuser = db.Column(db.Boolean, default=False)

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

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_superuser': self.is_superuser
        }

    def __repr__(self):
        return f'User(id: {self.id}, username: {self.username}. email: {self.email})'
