def authenticate_user(email: str, psswd: str):
    from db.model import User # todo: worokoround circular import
    usr = User.query.filter_by(email=email).first()
    if usr and usr.password_is_valid(psswd):
        return usr
