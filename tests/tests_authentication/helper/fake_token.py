from rest_framework_simplejwt import tokens
from authentication.helper.token import JwToken, RefreshToken, AccessToken 
from authentication.helper.utils import *
from time import sleep


class FakeJwToken(JwToken):
    @property
    def valid(self):
        return self.make()

    @property
    def invalid(self, invalid_char='q'):
        valid_token = self.make()
        return valid_token + invalid_char

    @property
    def expired(self):
        self.payload['exp'] = 0
        token = str(self.payload)
        return token


class FakeAcessToken(FakeJwToken):
    token_type  = AccessToken.token_type

class FakeEmailVerificationToken(FakeJwToken):
    token_type = RefreshToken.token_type

class FakeRefreshToken(FakeJwToken):
    token_type = RefreshToken.token_type

    @property
    def blacklisted(self):
        RefreshToken.blacklist(self.valid)
        return self.valid

class FakeResetPwdToken:
    def __init__(self, user) -> None:
        self.user = user
        self.token = user.password_reset_token

    @property
    def valid(self):
        return self.token.make()

    @property
    def invalid(self, invalid_char='q'):
        return self.valid + invalid_char

    @property
    def expired(self):
        token = self.token.make()
        sleep(1)
        return token

    @property
    def used(self):
        """
        overwrite user password -> make the token useless
        """
        token = self.token.make()
        self.user.set_password('new_secret_password')
        self.user.save()
        return token
    
    def same_as_old(self, old_password):
        self.user.set_password(old_password)
        self.user.save()
        return self.token.make()
