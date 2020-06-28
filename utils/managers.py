from typing import List

from db.model import User, UserGroup, InstructionDocument, InstructionDocumentPage
from repository.base import ObjectNotFoundError
from repository.repos import GroupUserRepository, InstructionDocumentPageRepository, UserRepository, \
    InstructionDocumentRepository


# todo: docs -> manager for existing objects


class UserManager:
    def __init__(self, user_id: int = None, user: User = None):
        self.__user_repo = UserRepository()
        self.__user = self.__user_repo.get(user_id) if user_id else user
        if not self.__user: raise ValueError(f'User not provided!')

    @property
    def user(self) -> User:
        return self.__user

    def belongs_to_group(self, group: UserGroup) -> bool:
        try:
            GroupUserRepository().get_by(user_id=self.__user.id, group_id=group.id)
            return True
        except ObjectNotFoundError:
            return False

    def delete(self):
        self.__user.is_deleted = True
        self.__user_repo.save(self.__user)


class InstructionDocumentManager:
    def __init__(self, document_id: int = None, document: InstructionDocument = None):
        self.__page_repo = InstructionDocumentPageRepository()
        self.__doc_repo = InstructionDocumentRepository()
        self.__document = self.__doc_repo.get(document_id) if document_id else document
        if not self.__document: raise ValueError(f'Document not provided!')

    def pages(self) -> List[InstructionDocumentPage]:
        return self.__page_repo.filter(InstructionDocumentPage.doc(self.__document.id))

    def page_count(self) -> int:
        return len(self.pages())

    def add_page(self, page: InstructionDocumentPage) -> InstructionDocumentPage:
        page.page_num = self.page_count() + 1
        self.__page_repo.save(page)
        return page

    def delete_page(self, page_num: int):
        page = self.__page_repo.get_by(document_id=self.__document.id, page_num=page_num)
        self.__page_repo.delete(page.id)
        for page in self.pages():
            if page.page_num > page_num:
                page.page_num = page.page_num - 1
                self.__page_repo.save(page)
