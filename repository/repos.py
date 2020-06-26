from db.model import InstructionDocument, User, GroupUser, UserGroup
from repository.base import Repository


class UserRepository(Repository):
    entity = User


class UserGroupRepository(Repository):
    entity = UserGroup


class GroupUserRepository(Repository):
    entity = GroupUser


class InstructionDocumentRepository(Repository):
    entity = InstructionDocument
