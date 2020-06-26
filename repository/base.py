from db.model import db


class ObjectNotFoundError(Exception): pass


class Repository:
    entity = NotImplemented

    def __init__(self):
        self.__session = db.session

    @property
    def session(self):
        return self.__session

    def get(self, entity_id: int):
        entity = self.session.query(self.entity).get(entity_id)
        if not entity: raise ObjectNotFoundError(f'{self.entity.__name__}[id: {entity_id}] not found.')
        return entity

    def get_by(self, **kwargs: int):
        entity = self.session.query(self.entity).filter_by(**kwargs).first()
        if not entity: raise ObjectNotFoundError(f'{self.entity.__name__}[{kwargs}] not found.')
        return entity

    def filter(self, f):
        return self.session.query(self.entity).filter(f).all()

    def save(self, entity):
        self.session.add(entity)
        self.session.commit()
