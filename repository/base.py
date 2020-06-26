from db.model import InstructionDocument, User


class ObjectNotFoundError(Exception): pass


class Repository:
    entity = NotImplemented

    def __init__(self, session):
        self.__session = session

    @property
    def session(self):
        return self.__session

    def get_by_id(self, entity_id):
        entity = self.session.query(self.entity).get(entity_id)
        if not entity: raise ObjectNotFoundError(f'{self.entity.__name__}[id: {entity_id}] not found.')

    def save(self, entity):
        self.session.add(entity)
        self.session.commit()


# example -> todo: move to separate files in /repository/<entity>_repository.py
class InstructionDocumentRepository(Repository):
    entity = InstructionDocument


class UserRepository(Repository):
    entity = User
