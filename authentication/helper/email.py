from django.core.mail import EmailMessage
from .link import VerifyRegistrationLink, get_domain_name, ResetPasswordLink
from .utils import raise_exception
from .token import EmailVerificationToken

ERROR_MSG = "Problème lors de l'envoi de l'e-mail, veuillez réessayer"

class Email:
    subject = ''
    message = ''

    @raise_exception(ERROR_MSG)
    def __init__(self, to):
        self.email =  EmailMessage (
            body = self.message,
            subject = self.subject, 
            to = [to.email]
        )

    @raise_exception(ERROR_MSG)
    def send(self):
        self.email.send()

class EmailwLink(Email):
    subject = 'Email avec un lien'
    message = ''' 
        Bonjour {username}, \n 
        Voici ton lien: \n
        {link}
    '''

    @raise_exception(ERROR_MSG)
    def __init__(self, to, request):
        self.create_link(to, request)
        self.message = self.message.format(username=to.username, link=self.link)
        super().__init__(to)

    def create_link(self, user, request):
        self.link = ''

class EmailVerification(EmailwLink):
    subject = 'Vérifie ton email'
    message = ''' 
        Bonjour {username}, \n 
        Nous somme heureux de te compter parmis les utilisateurs de ImpactED.
        Utilise le lien ci-dessous pour vérifier ton email: \n 
        {link}
    '''

    @raise_exception(ERROR_MSG)
    def create_link(self, user, request):
        domain = get_domain_name(request) 
        token = EmailVerificationToken(user).make()
        self.link = VerifyRegistrationLink(
            domain_name=domain, 
            parameters={'token':token}
        ).full_url


class EmailResetPassword(EmailwLink):
    subject = 'Réinisialise ton mot de passe'
    message = '''
        Bonjour {username}, \n 
        Utilises le lien ci-dessous pour réinitialiser ton mot de passe ImpactED: \n 
        {link}
    '''

    @raise_exception(ERROR_MSG)
    def create_link(self, user, request):
        domain = get_domain_name(request) 
        token = user.password_reset_token.make()
        uidb64 = user.get_uidb64()
        self.link = ResetPasswordLink(
            domain_name=domain, 
            path_variable={'uidb64':uidb64, 'token':token}
        ).full_url
