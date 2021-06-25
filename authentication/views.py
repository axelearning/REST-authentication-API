from rest_framework import generics, status, views, permissions
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import *
from .renderers import UserRenderer
from .helper.email import EmailVerification, EmailResetPassword
from .helper.token import JwToken


class RegisterAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.validated_data
        user = User.objects.get(email=user_data['email'])
        self.try_to_send_email_verification(user, request)

        response = {
            'email': user_data['email'],
            'username': user_data['username'],
            'is_student': user_data['is_student'],
            'is_teacher': user_data['is_teacher']
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def try_to_send_email_verification(self, user, request):
        try:
            EmailVerification(user, request).send()
        except:
            user.delete()
            raise Exception("Problème lors de l'envoi de l'e-mail, veuillez réessayer")

class RequestEmailVerificationAPI(generics.CreateAPIView):
    serializer_class = EmailSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        EmailVerification(user, request).send()

        return Response(
                "Un email a été envoyé afin de vérifier votre compte", 
                status = status.HTTP_200_OK
            )


class ConfirmEmailAPI(views.APIView):
    serializer_class = EmailVerificationSerializer
    renderer_classes = (UserRenderer, )

    # create a token field in swagger
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET['token']
        try:
            payload = JwToken.decode(token)
        except:
            return Response({'errors': 'Le token est expiré ou invalide'}, status=status.HTTP_403_FORBIDDEN)
        else:
            user = User.objects.get(id=payload['user_id'])
            user.email_verified = True
            user.save()
            return Response({'email': 'Compte activé'}, status=status.HTTP_200_OK)




class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RequestResetPasswordAPI(generics.GenericAPIView):
    serializer_class = EmailSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        """
        Send an email with a reset password link 
        pass a correct response even if the email doesn't exist
        ↳ goal: protect user from hacker who will try to find if an email is register or not
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data
        self.send_reset_password_email(user_data, request)
        
        return Response(
                {'email': f"Afin de réinitialiser votre mot de passe, un email a été envoyé à {user_data['email']}"}, 
                status = status.HTTP_200_OK
            )

    def send_reset_password_email(self, user_data, request):
        if User.objects.filter(email=user_data['email']).exists():
            user = User.objects.get(email=user_data['email'])
            EmailResetPassword(user, request).send()


class CheckPasswordTokenAPI(views.APIView):
    renderer_classes = (UserRenderer, )

    def get(self, _, uidb64, token):
            self.raise_invalid_link(uidb64, token)

            return Response(
                {
                    'message':' Valid Credentials', 
                    'uidb64': uidb64, 
                    'token': token
                }, 
                status=status.HTTP_200_OK
            )

    def raise_invalid_link(self, uidb64, token):
        try:
            user_id = decode_base64(uidb64)
            user =  User.objects.get(id=user_id)
            assert user and user.is_password_reset_token_valid(token)
        except:
            raise PermissionDenied({'link':"Le lien de réinitialisation n'est pas valide"})


class SetNewPasswordAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    renderer_classes = (UserRenderer, )

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        self.set_new_password(user_data)
        return Response({'password':'Réinitialisation du mot de passe réussie'}, status=status.HTTP_200_OK)

    def set_new_password(self, user_data):
        new_password = user_data['new_password']
        uidb64 = user_data['uidb64']
        id = decode_base64(uidb64)
        user = User.objects.get(id=id)
        user.set_password(new_password)
        user.save()


class LogoutAPI(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.blacklist_token()
        return Response(status=status.HTTP_204_NO_CONTENT)




