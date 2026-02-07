from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from hms.models import Student, Meal, Activity, Announcement, MaintenanceRequest, AuditLog

class Command(BaseCommand):
    help = 'Setup system roles and permissions'

    def handle(self, *args, **kwargs):
        roles = {
            'Admin': {
                'models': [Student, Meal, Activity, Announcement, MaintenanceRequest, AuditLog],
                'perms': ['add', 'change', 'delete', 'view', 'export'] # 'export' is custom
            },
            'Warden': {
                'models': [Student, Meal, MaintenanceRequest, Announcement],
                'perms': ['add', 'change', 'view']
            },
            'Finance': {
                'models': [AuditLog], # Placeholder
                'perms': ['view', 'export']
            },
            'Viewer': {
                'models': [Student, Meal, Activity, Announcement, MaintenanceRequest],
                'perms': ['view']
            }
        }

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            else:
                self.stdout.write(f'Updated group: {role_name}')
            
            # Clear existing permissions to reset
            group.permissions.clear()

            for model in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                for perm_code in config['perms']:
                    codename = f"{perm_code}_{model._meta.model_name}"
                    
                    # Handle custom permissions or standard ones
                    try:
                        perm = Permission.objects.get(content_type=content_type, codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write(f"  + Added {codename} to {role_name}")
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"  - Permission {codename} not found (might need migration)"))

        self.stdout.write(self.style.SUCCESS('Successfully Setup Roles and Permissions'))
