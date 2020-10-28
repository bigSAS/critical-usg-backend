from cusg.db.schema import InstructionDocument, User, GroupUser, UserGroup, InstructionDocumentPage
from cusg.repository.base import Repository


class UserRepository(Repository):
    entity = User

    def delete(self, entity_id: int):
        raise ValueError('User repository cannot delete users!')


class UserGroupRepository(Repository):
    entity = UserGroup


class GroupUserRepository(Repository):
    entity = GroupUser


class InstructionDocumentRepository(Repository):
    entity = InstructionDocument


class InstructionDocumentPageRepository(Repository):
    entity = InstructionDocumentPage
