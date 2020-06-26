from wsgi import app
from db.model import User, UserGroup, GroupUser
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
        # todo: SerializationError ???
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


class UserGroupSerializer(Serializer):
    fields = ('id', 'name')


if __name__ == '__main__':
    with app.app_context():
        user = UserRepository().get(1)
        s = UserSerializer(user)
        print(s.data)

