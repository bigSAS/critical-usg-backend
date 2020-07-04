from typing import List

from db.model import User, UserGroup, GroupUser, InstructionDocument
from repository.repos import GroupUserRepository, UserGroupRepository, UserRepository


class SerializationError(Exception): pass


class Serializer:
    fields = NotImplemented
    method_fields = []

    def __init__(self, obj):
        self.__object = obj

    def get_object(self):
        return self.__object

    @property
    def data(self):
        data = dict()
        try:
            for field in self.fields:
                obj = self.get_object()
                data[field] = getattr(obj, field)
            for mfield in self.method_fields:
                method = getattr(self, f'get_{mfield}')
                data[mfield] = method()
        except AttributeError as e:
            raise SerializationError(e)
        return data


class UserSerializer(Serializer):
    fields = ('id', 'email', 'username', 'is_superuser', 'is_deleted')
    method_fields = ('groups',)

    def get_groups(self):
        user_groups = GroupUserRepository().filter(GroupUser.user_id == self.get_object().id)
        group_ids = list(set([ug.group_id for ug in user_groups]))
        groups = UserGroupRepository().filter(UserGroup.id.in_(group_ids))
        return [UserGroupSerializer(g).data for g in groups]


class UserRelationSerializer(Serializer):
    fields = ('id', 'email', 'username', 'is_deleted')


class UserGroupSerializer(Serializer):
    fields = ('id', 'name')


class GroupUserSerializer(Serializer):
    fields = ('id', 'group_id', 'user_id')


class InstructionDocumentSerializer(Serializer):
    fields = ('id', 'name', 'description', 'created', 'updated')
    method_fields = ('created_by', 'updated_by')

    def get_created_by(self):
        o: InstructionDocument = self.get_object()
        usr: User = UserRepository().get(o.created_by_user_id)
        return UserRelationSerializer(usr).data

    def get_updated_by(self):
        o: InstructionDocument = self.get_object()
        usr: User = UserRepository().get(o.updated_by_user_id, ignore_not_found=True)
        if not usr: return None
        return UserRelationSerializer(usr).data


class InstructionDocumentPageSerializer(Serializer):
    fields = ('id', 'document_id', 'page_num', 'json')


class ListInstructionDocumentSerializer(Serializer):
    fields = ('page', 'prev_num', 'next_num', 'total')
    method_fields = ('results',)

    def get_results(self):
        return [InstructionDocumentSerializer(item).data for item in self.get_object().items]
