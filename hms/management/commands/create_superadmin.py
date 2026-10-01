from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hms.models import StaffProfile


class Command(BaseCommand):
    help = 'Creates or updates default Super Admin accounts with configured credentials.'

    def handle(self, *args, **options):
        admins = [
            {
                'username': 'Ali-Mahrez',
                'email': 'alimahrez744@gmail.com',
                'password': 'A8486aom',
                'national_id': 'SUPERADMIN001',
                'phone': '0750168458',
            },
            {
                'username': 'adminadmin',
                'email': 'admin@example.com',
                'password': 'A8486aom',
                'national_id': 'SUPERADMIN002',
                'phone': '0700000000',
            }
        ]

        for admin_data in admins:
            user, created = User.objects.get_or_create(
                username=admin_data['username'],
                defaults={
                    'email': admin_data['email'],
                    'is_superuser': True,
                    'is_staff': True,
                }
            )
            user.email = admin_data['email']
            user.is_superuser = True
            user.is_staff = True
            user.set_password(admin_data['password'])
            user.save()

            # Ensure StaffProfile exists
            StaffProfile.objects.update_or_create(
                user=user,
                defaults={
                    'role': 'super_admin',
                    'national_id': admin_data['national_id'],
                    'phone': admin_data['phone'],
                    'is_approved': True,
                }
            )

            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status} super admin: {user.username}"))
