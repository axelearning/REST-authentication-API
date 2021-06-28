from django.db import models
from django.contrib.auth.models import AbstractUser, User, UserManager
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .helper.token import AccessandRefreshToken, PasswordResetToken
from .helper.utils import encode_base64

# Create your models here.
class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('The given password must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    school = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True)
    bio = models.TextField(max_length=500, blank=True)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
      return self.email

    def get_uidb64(self) -> str:
        return encode_base64(self.id)

    @property
    def jwt_token(self):
        return AccessandRefreshToken(user=self)

    @property
    def password_reset_token(self):
        return PasswordResetToken(user=self)

    def is_password_same_has_old(self, new_password):
        return self.check_password(new_password)

    def is_password_reset_token_valid(self, token:str):
        return PasswordResetTokenGenerator().check_token(self, token)


# Create 2 kind of user: Student & Teacher 
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Student")

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Teacher")

