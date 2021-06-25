from rest_framework.test import APITestCase
from rest_framework.exceptions import PermissionDenied, ValidationError, AuthenticationFailed
from django.contrib.auth.hashers import check_password

from authentication.serializers import *
from authentication.models import *
from authentication.helper.utils import encode_base64
from .helper.fake_user import *
from .helper.fake_link import *
from .helper.fake_token import *



class TestRegister(APITestCase):
    
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
        serializer = RegisterSerializer(data=self.request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(email=serializer.data['email'])
        self.assertEqual(user.is_teacher, self.request['is_teacher'])
        self.assertEqual(user.is_student, self.request['is_student'])
        self.assertEqual(user.username, self.request['username'])
        self.assertTrue(check_password(self.request['password'], user.password))

    def test_multiple_role(self):
        self.request['is_student'] = True
        self.request['is_teacher'] = True
        serializer = RegisterSerializer(data=self.request)
        with self.assertRaisesMessage(ValidationError, "Faire un choix entre l'élève et l'enseignant"):
            serializer.is_valid(raise_exception=True)

    def test_no_role(self):
        self.request['is_student'] = False
        self.request['is_teacher'] = False
        serializer = RegisterSerializer(data=self.request)
        with self.assertRaisesMessage(ValidationError, "Faire un choix entre l'élève et l'enseignant"):
            serializer.is_valid(raise_exception=True)

class TestLogin(APITestCase):
    
    def setUp(self) -> None:
        self.request = {
        'username': generate_username(),
        'email': generate_email(),
        'password': generate_password(),
        }
        self.user = User.objects.create_user(**self.request)
        return super().setUp()

    def test_verified_user(self):
        self.user.email_verified = True
        self.user.save()
        serializer = LoginSerializer(data=self.request)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], self.user.email)
        self.assertEqual(serializer.validated_data['username'], self.user.username)
        tokens = serializer.validated_data['tokens']
        self.assertEqual(['access', 'refresh'], list(tokens.keys()))
        for token in tokens.values():
            self.assertTrue(isinstance(token, str))
        
    def test_unverified_user(self):
        self.user.email_verified = False
        self.user.save()
        serializer = LoginSerializer(data=self.request)
        with self.assertRaisesMessage(AuthenticationFailed, 'Confirm your email first'):
            serializer.is_valid()

    def test_ban_user(self):
        # ban user 
        self.user.is_active = False
        self.user.save()
        serializer = LoginSerializer(data=self.request)
        with self.assertRaisesMessage(AuthenticationFailed, 'Your account have been ban, please contact an admin'):
            serializer.is_valid()

    def test_invalid_user(self):
        self.user.email_verified = True
        self.user.save()
        self.request['password'] = 'thisPasswordIsInvalid'
        serializer = LoginSerializer(data=self.request)
        with self.assertRaisesMessage(AuthenticationFailed, 'Invalids Credentials'):
            serializer.is_valid()

class TestEmailVerification(APITestCase):

    def setUp(self) -> None:
        user = UserBackery().make()
        self.token = FakeEmailVerificationToken(user)
        return super().setUp()

    def test_valid_token(self):
        request = {
            'token': self.token.valid
        }
        serializer = EmailVerificationSerializer(data=request)
        self.assertTrue(serializer.is_valid())

class TestResetPassword(APITestCase):
    def test_valid_email(self):
        serializer = EmailSerializer(data={'email':generate_email()})
        self.assertTrue(serializer.is_valid())

    def test_invalid_email(self):
        serializer = EmailSerializer(data={'email':'wwe'})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

class TestSetNewPassword(APITestCase):

    def setUp(self) -> None:
        user = UserBackery().make()
        self.token = FakeResetPwdToken(user)
        self.uidb64 = user.get_uidb64()
        self.password = generate_password()
        self.request = {
            'new_password': self.password,
            'token': self.token.valid,
            'uidb64': self.uidb64
        }
        return super().setUp()

    def test_valid_credentials(self):
        serializer = SetNewPasswordSerializer(data=self.request)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(self.uidb64, serializer.validated_data['uidb64'])
        self.assertEqual(self.token.valid, serializer.validated_data['token'])
        self.assertEqual(self.password, serializer.validated_data['new_password'])

    def test_invalid_id(self):
        invalid_uidb64 = encode_base64(-1)
        self.request['uidb64'] = invalid_uidb64
        serializer = SetNewPasswordSerializer(data=self.request)
        with self.assertRaisesMessage(AuthenticationFailed, 'Invalids Id'):
            serializer.is_valid(raise_exception=True)

    def test_invalid_token(self):
        self.request['token'] = self.token.invalid
        serializer = SetNewPasswordSerializer(data=self.request)
        with self.assertRaisesMessage(PermissionDenied, "Le lien de réinitialisation n'est pas valide"):
            serializer.is_valid(raise_exception=True)

    def test_same_password_as_old(self):
        token = self.token.same_as_old(old_password=self.password)
        self.request['token'] = token
        serializer = SetNewPasswordSerializer(data=self.request)
        with self.assertRaisesMessage(PermissionDenied, 'Vous avez déjà utilisé ce mot de passe'):
            serializer.is_valid(raise_exception=True)

class TestLogout(APITestCase):
    
    def setUp(self) -> None:
        user = UserBackery().make()
        self.token = FakeRefreshToken(user)
        return super().setUp()

    def test_valid_token(self):
        request = {
            'refresh': self.token.valid
        }
        serializer = LogoutSerializer(data=request)
        serializer.is_valid(raise_exception=True)
        serializer.blacklist_token()

    def test_no_token(self):
        request = {
            'refresh': ''
        }
        serializer = LogoutSerializer(data=request)
        with self.assertRaisesMessage(ValidationError, 'Ce champ ne peut être vide.'):
            serializer.is_valid(raise_exception=True)

    def test_invalid_token(self):
        request = {
            'refresh': self.token.invalid
        }
        serializer = LogoutSerializer(data=request)
        serializer.is_valid(raise_exception=True)
        with self.assertRaisesMessage(ValidationError, 'Le token est expiré ou invalide'):
            serializer.blacklist_token()

    def test_expired_token(self):
        user_data = {
            'refresh': self.token.expired
        }
        serializer = LogoutSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        with self.assertRaisesMessage(ValidationError, 'Le token est expiré ou invalide'):
            serializer.blacklist_token()


