from authentication.helper.link import VerifyRegistrationLink, ResetPasswordLink

class FakeLink:
    '''
    Link need to be different when we test the API we only need 
    the path and query_string 
    '''
    def __init__(self):
        pass

    def make(self):
        url  = self.link.path + self.link.query_string 
        return url

class FakeEmailVerifLink(FakeLink):
    def __init__(self, token):
        self.link = VerifyRegistrationLink('', parameters = {'token': token})

class FakeResetPasswordLink(FakeLink):
    def __init__(self, uidb64, token):
        self.link = ResetPasswordLink('', path_variable = {'uidb64':uidb64, 'token': token})
        self.link.query_string = ''