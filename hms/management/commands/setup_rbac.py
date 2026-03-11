from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Setup Role-Based Access Control Groups and Permissions'

    def handle(self, *args, **options):
        roles = {
            'Super Admin': {
                'permissions': '__all__',
            },
            'Welfare Officer': {
                'permissions': [
                    'view_student', 'change_student',
                    'view_defermentrequest', 'change_defermentrequest',
                    'view_announcement', 'add_announcement', 'change_announcement',
                    'view_auditlog',
                ]
            },
            'Hostel Manager': {
                'permissions': [
                    'view_room', 'add_room', 'change_room',
                    'view_roomassignment', 'add_roomassignment', 'change_roomassignment',
                    'view_roomchangerequest', 'change_roomchangerequest',
                    'view_student',
                ]
            },
            'Kitchen Manager': {
                'permissions': [
                    'view_meal', 'add_meal', 'change_meal',
                    'view_activity', 'add_activity', 'change_activity',
                    'view_announcement',
                ]
            },
            'Security': {
                'permissions': [
                    'view_visitor', 'add_visitor', 'change_visitor',
                    'view_student',
                ]
            },
            'Student': {
                'permissions': [
                    'view_student', 'change_student',
                    'add_maintenancerequest', 'view_maintenancerequest',
                    'add_tutoringpost', 'view_tutoringpost', 'delete_tutoringpost',
                    'view_meal', 'add_meal',
                    'view_announcement',
                ]
            }
        }

        hms_content_types = ContentType.objects.filter(app_label='hms')
        all_permissions = Permission.objects.filter(content_type__in=hms_content_types)

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            else:
                self.stdout.write(f'Group already exists: {role_name}')
                group.permissions.clear()

            if config['permissions'] == '__all__':
                group.permissions.set(all_permissions)
                self.stdout.write(f'Assigned all hms permissions to {role_name}')
            else:
                perms = all_permissions.filter(codename__in=config['permissions'])
                group.permissions.set(perms)
                self.stdout.write(f'Assigned {perms.count()} permissions to {role_name}')

        self.stdout.write(self.style.SUCCESS('RBAC Setup Completed Successfully'))
