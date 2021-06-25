from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.test.utils import override_settings

from .helper.fake_token import *
from .helper.fake_user import *
from .helper.fake_link import *
from authentication.helper.utils import encode_base64

class TestRegister(APITestCase):
    url = reverse('register')

    def setUp(self) -> None:
        self.request = {
            'email': generate_email(),
            'username': generate_username(),
            'password': generate_password(),
            'is_student': True,
            'is_teacher': False
        }
        return super().setUp()

    def test_valid_data(self):
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_data(self):
        request = {}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_role(self):
        self.request.update({
            'is_student': True,
            'is_teacher': True,
        })
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_role(self):
        self.request.update({
            'is_student': False,
            'is_teacher': False,
        })
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class RequestEmailVerification(APITestCase):
    url = reverse('email-verify-request')

    def setUp(self) -> None:
        self.email = generate_email()
        UserBackery(email=self.email).make()

    def test_valid_email(self):
        request = {"email": self.email}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_email(self):
        request = {"email": 'NotAnEmailField'}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        request = {"email": ''}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestConfirmEmailVerify(APITestCase):

    def setUp(self) -> None:
        user = UserBackery().make()
        self.token = FakeEmailVerificationToken(user)
        return super().setUp()

    def test_valid_token(self):
        url = FakeEmailVerifLink(self.token.valid).make()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        url = FakeEmailVerifLink(self.token.invalid).make()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expired_token(self):
        url = FakeEmailVerifLink(self.token.expired).make()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLogin(APITestCase):
    url = reverse('login')

    def setUp(self) -> None:
        self.user = UserBackery().make()
        self.password = generate_password()
        self.user.set_password(self.password)
        self.user.save()
        self.request = {
            'email': self.user.email, 
            'password': self.password
        }
        return super().setUp()

    def test_verified_user(self):
        self.user.email_verified = True
        self.user.save()
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unverified_email(self):
        self.user.email_verified = False
        self.user.save()
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ban_user(self):
        self.user.email_verified = True
        self.user.is_active = False # ban user
        self.user.save()
        response = self.client.post(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestRequestNewPassword(APITestCase):
    url = reverse('password-reset-request')

    def test_valid_email(self):
        user = UserBackery().make()
        request = {'email':user.email}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsigned_email(self):
        """"
        Why a 200 status code (HTTP_OK) ?
        ↳ trap hacker with a correct status code even for unsigned email
        """
        unsigned_email = generate_email()
        request = {'email': unsigned_email}
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_email(self):
        invalid_email = {'email': 'not_an_email_fields'}
        response = self.client.post(self.url, invalid_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestPasswordResetConfirm(APITestCase):

    def setUp(self):
        user = UserBackery().make()
        self.uidb64 = user.get_uidb64()
        self.token = FakeResetPwdToken(user)
        return super().setUp()

    def test_valid_link(self):
        request = FakeResetPasswordLink(self.uidb64, self.token.valid).make()
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        invalid_token = self.token.invalid
        request = FakeResetPasswordLink(self.uidb64, invalid_token).make()
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(PASSWORD_RESET_TIMEOUT=0)
    def test_expired_token(self):
        expired_token = self.token.expired
        request = FakeResetPasswordLink(self.uidb64, expired_token).make()
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_id(self):
        invalid_uidb64 = encode_base64(-1)
        request = FakeResetPasswordLink(invalid_uidb64, self.token.valid).make()
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestPasswordResetComplete(APITestCase):
    url = reverse('password-reset-complete')

    def setUp(self):
        user = UserBackery().make()
        self.token = FakeResetPwdToken(user)
        self.uidb64 = user.get_uidb64()
        self.request = {
            "new_password": generate_password(),
            "token": self.token.valid,
            "uidb64": self.uidb64
        }
        return super().setUp()
    
    def test_valid_credentials(self):
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        self.request['token'] = self.token.invalid
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(PASSWORD_RESET_TIMEOUT=0)
    def test_expired_token(self):
        self.request['token'] = self.token.expired
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_used_token(self): 
        self.request['token'] = self.token.used
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_id(self):
        invalid_uidb64 = encode_base64(-1)
        self.request['uidb64'] = invalid_uidb64
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_password(self):
        self.request['new_password'] = 'short'
        response = self.client.patch(self.url, self.request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestRefreshJwToken(APITestCase):
    url = reverse('token_refresh')

    def setUp(self):
        user = UserBackery().make()
        self.token = FakeRefreshToken(user)
        return super().setUp()

    def test_valid_token(self):
        request = {
            'refresh': self.token.valid
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        request = {
            'refresh': self.token.invalid
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_token(self):
        request = {
            'refresh': self.token.expired
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklisted_token(self):
        request = {
            'refresh': self.token.blacklisted
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestLogout(APITestCase):
    url = reverse('logout')

    def setUp(self):
        user = UserBackery().make()
        self.client.force_login(user)
        self.token = FakeRefreshToken(user)
        return super().setUp()

    def test_valid_token(self):
        request = {
            'refresh': self.token.valid
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_token(self):
        request = {
            'refresh': self.token.invalid
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_token(self):
        request = {
            'refresh': self.token.expired
        }
        response = self.client.post(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)