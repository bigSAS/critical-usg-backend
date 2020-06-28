from db.model import User, UserGroup, InstructionDocument, InstructionDocumentPage
from repository.base import ObjectNotFoundError
from repository.repos import GroupUserRepository, InstructionDocumentPageRepository


class UserManager:
    def __init__(self, user: User):
        self.__user = user

    def belongs_to_group(self, group: UserGroup):
        try:
            GroupUserRepository().get_by(user_id=self.__user.id, group_id=group.id)
            return True
        except ObjectNotFoundError:
            return False


class InstructionDocumentManager:
    def __init__(self, document: InstructionDocument):
        self.__document = document

    def page_count(self):
        return len(InstructionDocumentPageRepository().filter(InstructionDocumentPage.doc(self.__document.id)))
