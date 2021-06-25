from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt import tokens as simple_jwt
from rest_framework_simplejwt.backends import TokenBackend

SECRET_KEY = settings.SECRET_KEY
ALGORTIHM = settings.ALGORTIHM

class JwToken:
    token_type = simple_jwt.Token

    def __init__(self, user=None):
        if user:
            self.payload = self.token_type.for_user(user)

    def make(self):
        if not self.payload:
            raise ValueError('Pass a user to the constructor when you call make()')
        else:
            return str(self.payload)

    @staticmethod
    def decode(token):
        payload = TokenBackend(algorithm=ALGORTIHM, signing_key=SECRET_KEY).decode(token)
        return payload
    
    @staticmethod
    def encode(payload):
        return  str(payload)


class AccessToken(JwToken):
    token_type = simple_jwt.AccessToken

class RefreshToken(JwToken):
    token_type = simple_jwt.RefreshToken

    @staticmethod
    def blacklist(token):
        try:
            simple_jwt.RefreshToken(token).blacklist()
        except:
            raise simple_jwt.TokenError('Token is expired or invalid')

class EmailVerificationToken(RefreshToken):
    '''
    Token send to verify user's email
    '''
    pass


class AccessandRefreshToken(RefreshToken):
    def __init__(self, user):
        super().__init__(user=user)
        self.refresh_payload = self.payload
        self.access_payload = self.refresh_payload.access_token

    def generate(self):
        self.refresh = str(self.refresh_payload)
        self.access = str(self.access_payload)
        return self


class PasswordResetToken:
    def __init__(self, user):
        self.user = user

    def make(self):
        return PasswordResetTokenGenerator().make_token(self.user)




