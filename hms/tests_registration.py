from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from hms.models import Student

class RegistrationTermsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('hms:register')
        self.registration_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test@example.com',
            'university_id': 'SD06/PU/30104/25',
            'phone': '0712345678',
            'gender': 'male',
            'program_of_study': 'Computer Science',
            'disability': 'none',
            'county': 'nairobi',
            'residence_type': 'hostel',
            'hostel': '1',
            'room_number': '201',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }

    def test_registration_fails_without_terms(self):
        """Test that registration fails if terms are not accepted."""
        data = self.registration_data.copy()
        # terms field is not included, or False
        response = self.client.post(self.register_url, data)
        
        # Should return to registration page with error
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('terms', form.errors)
        self.assertEqual(form.errors['terms'], ['You must agree to the terms and conditions to register.'])
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    def test_registration_succeeds_with_terms(self):
        """Test that registration succeeds if terms are accepted."""
        data = self.registration_data.copy()
        data['terms'] = 'on'  # Checkboxes in forms usually send 'on'
        response = self.client.post(self.register_url, data)
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        self.assertTrue(Student.objects.filter(user__email='test@example.com').exists())
