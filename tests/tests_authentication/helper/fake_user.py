from model_bakery import baker
from faker import Faker

from authentication.models import User

class UserBackery:
    _FIELDS = {}

    def __init__(self, **kwargs):
        self.fields = self._FIELDS.copy()
        extended_fields = {key:value for key,value in kwargs.items()}
        self.fields.update(extended_fields)

    def make(self):
        return baker.make(User, **self.fields)


class FakeStudent(UserBackery):
    _FIELDS = {
        'is_student': True,
        'is_teacher': False,
    }

class FakeTeacher(UserBackery):
    _FIELDS = {
        'is_student': False,
        'is_teacher': True,
    }

class UserWithNoRole(UserBackery):
    _FIELDS = {
        'is_student': False,
        'is_teacher': False,
    }

class UserWithMultipleRole(UserBackery):
    _FIELDS = {
        'is_student': True,
        'is_teacher': True,
    }


def generate_email():
    return Faker().email()

def generate_password():
    return Faker().email()

def generate_username():
    return Faker().email().split('@')[0]






