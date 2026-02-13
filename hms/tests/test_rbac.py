from django.test import TestCase
from django.contrib.auth.models import User
from hms.models import StaffProfile
from hms.decorators import role_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

class RBACTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teststaff', password='password123')
        self.profile = StaffProfile.objects.create(
            user=self.user,
            role='DEAN_AGRICULTURE',
            national_id='12345678',
            phone='0700000000'
        )

    def test_role_categorization(self):
        """Test that roles are correctly mapped to categories"""
        # Agriculture Dean should be ACADEMIC_ADMIN
        self.assertEqual(self.profile.get_category(), 'ACADEMIC_ADMIN')
        
        # Test a Finance role
        self.profile.role = 'INTERNAL_AUDITOR'
        self.profile.save()
        self.assertEqual(self.profile.get_category(), 'FINANCE_ADMIN')
        
        # Test an Executive role
        self.profile.role = 'VICE_CHANCELLOR'
        self.profile.save()
        self.assertEqual(self.profile.get_category(), 'EXECUTIVE')

    def test_role_required_decorator_with_categories(self):
        """Test the decorator with allowed_categories"""
        
        @role_required(allowed_categories=['ACADEMIC_ADMIN'])
        def dummy_view(request):
            return "Success"

        # 1. Access granted (Academic Admin)
        self.profile.role = 'DEAN_AGRICULTURE'
        self.profile.save()
        request = HttpRequest()
        request.user = self.user
        self.assertEqual(dummy_view(request), "Success")

        # 2. Access denied (Finance Admin)
        self.profile.role = 'INTERNAL_AUDITOR'
        self.profile.save()
        with self.assertRaises(PermissionDenied):
            dummy_view(request)

        # 3. Superuser should always have access
        self.user.is_superuser = True
        self.user.save()
        self.assertEqual(dummy_view(request), "Success")

    def test_staff_registration_form_searchable_role(self):
        """Test that the form correctly handles typed roles"""
        from hms.forms import StaffRegistrationForm
        
        # 1. Valid by Value
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'pass',
            'confirm_password': 'pass',
            'role': 'VICE_CHANCELLOR',
            'national_id': 'ID123',
            'phone': '0700000000'
        }
        form = StaffRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['role'], 'VICE_CHANCELLOR')

        # 2. Valid by Label (typing the human-readable string)
        form_data['role'] = 'Vice Chancellor'
        form_data['email'] = 'john2@example.com' # must be unique
        form = StaffRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['role'], 'VICE_CHANCELLOR')

        # 3. Invalid role
        form_data['role'] = 'Invalid Role'
        form_data['email'] = 'john3@example.com'
        form = StaffRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
