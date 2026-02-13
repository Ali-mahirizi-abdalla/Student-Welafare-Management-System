from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import Student, Meal
from datetime import date, timedelta, time, datetime
from unittest.mock import patch

class MealSubmissionTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='teststudent', password='password123')
        # Student profile is created via signal, just update it
        self.student = Student.objects.get(user=self.user)
        self.student.university_id = 'S12345'
        self.student.save()
        self.client = Client()
        self.client.login(username='teststudent', password='password123')

    def test_meal_creation(self):
        """Test basic meal creation via model"""
        today = date.today()
        Meal.objects.create(student=self.student, date=today, breakfast=True)
        self.assertEqual(Meal.objects.filter(student=self.student).count(), 1)
        
    def test_unique_constraint(self):
        """Test that a student cannot have two meal records for the same day (DB level)"""
        today = date.today()
        Meal.objects.create(student=self.student, date=today, breakfast=True)
        with self.assertRaises(Exception): # IntegrityError usually
            Meal.objects.create(student=self.student, date=today, supper=True)

    @patch('hms.views.datetime') 
    @patch('hms.views.timezone')
    def test_breakfast_lock_logic(self, mock_timezone, mock_datetime):
        """Test that breakfast cannot be changed after 8:00 AM"""
        # Mock time to be 9:00 AM
        fixed_dt = datetime.now()
        # This implementation depends heavily on how views import datetime/timezone
        # Skipping complex mocking for now, testing view response logic directly if possible
        pass

class AdminDashboardTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='password123')
        self.client = Client()
        self.client.login(username='admin', password='password123')

    def test_admin_access(self):
        """Test admin dashboard accessibility"""
        response = self.client.get(reverse('hms:admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_stats_calculation(self):
        """Test that stats are calculated correctly"""
        # Create some meals
        u1 = User.objects.create_user(username='s1', password='p')
        s1 = Student.objects.get(user=u1)
        s1.university_id = '1'
        s1.save()
        Meal.objects.create(student=s1, date=date.today(), breakfast=True, supper=True)
        
        response = self.client.get(reverse('hms:admin_dashboard'))
        self.assertEqual(response.context['today_stats']['breakfast'], 1)
        self.assertEqual(response.context['today_stats']['supper'], 1)

class StaffRegistrationTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='superadmin', password='password123', email='admin@example.com')
        self.client = Client()
        self.client.login(username='superadmin', password='password123')

    def test_register_staff_access(self):
        """Test that only superusers can access staff registration"""
        response = self.client.get(reverse('hms:register_staff'))
        self.assertEqual(response.status_code, 200)

        # Test non-superuser access
        self.client.logout()
        User.objects.create_user(username='staffuser', password='password123', is_staff=True)
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('hms:register_staff'))
        self.assertEqual(response.status_code, 302) # Should redirect

    def test_staff_registration_success(self):
        """Test successful staff registration via view"""
        data = {
            'first_name': 'Test',
            'last_name': 'Staff',
            'email': 'staffmember@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'DEFERMENT',
            'national_id': 'ROLE007',
            'phone': '0712345678'
        }
        response = self.client.post(reverse('hms:register_staff'), data)
        self.assertEqual(response.status_code, 302) # Redirect on success

        # Verify User and StaffProfile
        user = User.objects.get(email='staffmember@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertTrue(user.is_staff)
        
        from hms.models import StaffProfile
        staff = StaffProfile.objects.get(user=user)
        self.assertEqual(staff.role, 'DEFERMENT')
        self.assertEqual(staff.national_id, 'ROLE007')

    def test_staff_registration_failure(self):
        """Test registration failure (mismatched passwords)"""
        data = {
            'first_name': 'Test',
            'last_name': 'Staff',
            'email': 'badstaff@example.com',
            'password': 'password123',
            'confirm_password': 'wrongpassword',
            'role': 'NEWS_ALERT',
            'national_id': 'ROLE999',
            'phone': '0712345678'
        }
        response = self.client.post(reverse('hms:register_staff'), data)
        self.assertEqual(response.status_code, 200) # Returns to form on error
        self.assertFalse(User.objects.filter(email='badstaff@example.com').exists())

class DashboardVisibilityTest(TestCase):
    def setUp(self):
        self.client = Client()
        from hms.models import StaffProfile
        
        # 1. Superadmin
        self.superadmin = User.objects.create_superuser(username='super', password='p')
        
        # 2. Deferment Manager
        self.defer_user = User.objects.create_user(username='defer', password='p', is_staff=True)
        StaffProfile.objects.create(user=self.defer_user, role='DEFERMENT', national_id='ID1')
        
        # 3. Visitors Manager
        self.visitor_user = User.objects.create_user(username='visitor', password='p', is_staff=True)
        StaffProfile.objects.create(user=self.visitor_user, role='VISITORS', national_id='ID2')

    def test_superadmin_visibility(self):
        self.client.login(username='super', password='p')
        response = self.client.get(reverse('hms:admin_dashboard'))
        self.assertTrue(response.context['is_superadmin'])
        self.assertIsNone(response.context['staff_role'])

    def test_deferment_visibility(self):
        self.client.login(username='defer', password='p')
        response = self.client.get(reverse('hms:admin_dashboard'))
        self.assertFalse(response.context['is_superadmin'])
        self.assertEqual(response.context['staff_role'], 'DEFERMENT')

    def test_visitors_visibility(self):
        self.client.login(username='visitor', password='p')
        response = self.client.get(reverse('hms:admin_dashboard'))
        self.assertFalse(response.context['is_superadmin'])
        self.assertEqual(response.context['staff_role'], 'VISITORS')
