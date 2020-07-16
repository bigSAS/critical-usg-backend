from repository.repos import UserGroupRepository
from wsgi import app
from db.model import db, UserGroup

DEFAULT_USER_GROUPS = ('USER', 'ADMIN')


def create_default_groups():
    with app.app_context():
        print('Create default user groups')
        created_groups = []
        for user_group in DEFAULT_USER_GROUPS:
            existing_ug = UserGroupRepository().get_by(name=user_group, ignore_not_found=True)
            if not existing_ug:
                user_group = UserGroup(name=user_group)
                UserGroupRepository().save(user_group)
                created_groups.append(user_group)
        db.session.commit()
        if len(created_groups) > 0:
            print(f'Created {len(created_groups)}:', created_groups)
        else:
            print('No new user groups created...')


if __name__ == '__main__':
    create_default_groups()
