from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from .utils import raise_exception

def get_domain_name(request):
    return get_current_site(request).domain

def generate_query_string(parameters):
        list_of_parameters = [f'{key}={value}' for key, value in parameters.items()]
        parameters = '&'.join(list_of_parameters)
        query_string =  '?' + parameters
        return query_string

class LinkGenerator:
    PROTOCOL = 'http://'
    PATH_NAME = ''

    @raise_exception(message='Problem when we generate the link')
    def __init__(self, domain_name, path_variable=None, parameters=None):
        self.domain_name = domain_name
        self.path = self.generate_path(path_variable)
        self.full_url = self.PROTOCOL + self.domain_name + self.path

        if parameters:
            self.query_string = generate_query_string(parameters) 
            self.full_url += self.query_string


    def generate_path(self, path_variable):
        path = reverse(self.PATH_NAME, kwargs= path_variable)
        return path

class VerifyRegistrationLink(LinkGenerator):
    PATH_NAME = 'email-verify-confirm'

class ResetPasswordLink(LinkGenerator):
    PATH_NAME = 'password-reset-confirm'

