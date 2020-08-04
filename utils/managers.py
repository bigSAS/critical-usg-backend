from typing import List
from datetime import datetime

from db.models import UserEntityModel, UserGroupEntityModel
from db.schema import User, UserGroup, InstructionDocument, InstructionDocumentPage, GroupUser
from repository.base import ObjectNotFoundError
from repository.repos import GroupUserRepository, InstructionDocumentPageRepository, UserRepository, \
    InstructionDocumentRepository, UserGroupRepository


class UserManager:
    def __init__(self, user_id: int = None, user: User = None):
        self.__user_repo = UserRepository()
        self.__user = self.__user_repo.get(user_id) if user_id else user
        if not self.__user: raise ValueError('User not provided!')

    @property
    def user(self) -> User:
        return self.__user

    @property
    def user_model(self) -> UserEntityModel:
        return UserEntityModel.construct(
            id=self.user.id,
            username=self.user.username,
            email=self.user.email,
            is_superuser=self.user.is_superuser,
            is_deleted=self.user.is_deleted,
            groups=[UserGroupEntityModel.construct(id=g.id, name=g.name) for g in self.get_groups()]
        )

    def get_groups(self) -> List[UserGroup]:
        user_groups = GroupUserRepository().filter(GroupUser.user_id == self.user.id)
        group_ids = list(set([ug.group_id for ug in user_groups]))
        return UserGroupRepository().filter(UserGroup.id.in_(group_ids))

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
        if not self.__document: raise ValueError('Document not provided!')

    @property
    def document(self):
        return self.__document

    def update(self, user_id: int, **kwargs):
        valid_kwargs = ('name', 'description')
        for k, v in kwargs.items():
            if k in valid_kwargs: setattr(self.__document, k, v)
        self.__document.updated_by_user_id = user_id
        self.__document.updated = datetime.utcnow()
        self.__doc_repo.save(self.__document)

    def pages(self) -> List[InstructionDocumentPage]:
        return self.__page_repo.filter(InstructionDocumentPage.doc(self.__document.id))

    def page_count(self) -> int:
        return len(self.pages())

    def add_page(self, page: InstructionDocumentPage, user_id: int) -> InstructionDocumentPage:
        page.page_num = self.page_count() + 1
        self.__page_repo.save(page)
        self.__document.updated_by_user_id = user_id
        self.__document.updated = datetime.utcnow()
        self.__doc_repo.save(self.__document)
        return page

    def delete_page(self, user_id: int, page_num: int):
        page = self.__page_repo.get_by(document_id=self.__document.id, page_num=page_num)
        self.__page_repo.delete(page.id)
        for page in self.pages():
            if page.page_num > page_num:
                page.page_num = page.page_num - 1
                self.__page_repo.save(page)

        self.__document.updated_by_user_id = user_id
        self.__document.updated = datetime.utcnow()
        self.__doc_repo.save(self.__document)
