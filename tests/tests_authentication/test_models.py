from rest_framework.test import APITestCase
from authentication.models import User

FIELDS = {
        'username': 'axelito',
        'email': 'axelito@gmail.com',
        'password': 'secret_password',
    }

class TestModel(APITestCase):

    def test_create_user(self):
        user = User.objects.create_user(**FIELDS)
        self.assertIsInstance(user, User)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.email, FIELDS['email'])
        self.assertEqual(user.username, FIELDS['username'])
        self.assertTrue(user.check_password(FIELDS['password']))

    def test_super_user(self):
        user = User.objects.create_superuser(**FIELDS)
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, FIELDS['email'])
        self.assertEqual(user.username, FIELDS['username'])
        self.assertTrue(user.check_password(FIELDS['password']))

    def test_raise_error_with_empty_username(self):
        missing_fields = FIELDS.copy()
        missing_fields['username'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**missing_fields)

    def test_raise_error_with_empty_email(self):
        missing_fields = FIELDS.copy()
        missing_fields['email'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**missing_fields)

    def test_raise_error_with_empty_password(self):
        missing_fields = FIELDS.copy()
        missing_fields['password'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**missing_fields)

