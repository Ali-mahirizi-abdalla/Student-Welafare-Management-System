from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class EmailLoginTest(TestCase):
    def setUp(self):
        # Create a user with a specific username and email
        self.username = 'testuser'
        self.email = 'test@example.com'
        self.password = 'Password123!'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_login_with_username(self):
        """Test that authentication still works with the standard username"""
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.username)

    def test_login_with_email(self):
        """Test that authentication works using the email address instead of username"""
        user = authenticate(username=self.email, password=self.password)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.username, self.username)

    def test_login_with_invalid_credentials(self):
        """Test that authentication fails with incorrect credentials"""
        user = authenticate(username=self.email, password='WrongPassword')
        self.assertIsNone(user)
        
        user = authenticate(username='nonexistent@example.com', password=self.password)
        self.assertIsNone(user)
