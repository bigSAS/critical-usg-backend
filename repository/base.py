from sqlalchemy import text

from db.model import db


class ObjectNotFoundError(Exception): pass


class Repository:
    entity = NotImplemented

    def __init__(self):
        self.__session = db.session

    @property
    def session(self):
        return self.__session

    def get(self, entity_id: int, ignore_not_found: bool = False):
        entity = self.session.query(self.entity).get(entity_id)
        if not entity and not ignore_not_found:
            raise ObjectNotFoundError(f'{self.entity.__name__}[id: {entity_id}] not found.')
        return entity

    def get_by(self, **kwargs):
        ignore_not_found = kwargs.pop('ignore_not_found', False)
        entity = self.session.query(self.entity).filter_by(**kwargs).first()
        if not entity and not ignore_not_found:
            raise ObjectNotFoundError(f'{self.entity.__name__}[{kwargs}] not found.')
        return entity

    def filter(self, f, order: str = None):
        if order: return self.session.query(self.entity).filter(f).order_by(text(order)).all()
        return self.session.query(self.entity).filter(f).all()

    def save(self, entity):
        self.session.add(entity)
        self.session.commit()
