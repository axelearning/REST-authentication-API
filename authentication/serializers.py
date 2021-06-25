from django.contrib.auth.hashers import make_password
from django.contrib import auth

from rest_framework import serializers, exceptions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.tokens import TokenError

from .models import User, Student, Teacher
from .helper.token import AccessandRefreshToken, RefreshToken
from .helper.utils import decode_base64


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_student', 'is_teacher')

    def validate(self, data):
        '''
        Check if the user is either a teacher or a student, not BOTH or NEITHER [XOR]
            ↳ add this custom validation to is.valid() serializer method
        '''
        role_counter = data['is_student'] + data['is_teacher']
        if role_counter != 1:
            raise exceptions.ValidationError({'one_role':"Faire un choix entre l'élève et l'enseignant"})
        return data

    def create(self, validated_data, *args, **kwargs):
        password = validated_data.pop('password')
        hash = make_password(password)
        user = User.objects.create(**validated_data, password=hash)

        if validated_data['is_student']:
            Student.objects.create(user=user)
        if  validated_data['is_teacher']:
            Teacher.objects.create(user=user)
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ('token',)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField(method_name='get_tokens')

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        tokens = AccessandRefreshToken(user).generate()
        return {
            'access': tokens.access,
            'refresh': tokens.refresh
        }

    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'tokens')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True},
            'tokens': {'read_only': True},
        }

    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')
        user = auth.authenticate(email=email, password=password)

        self._raise_invalid_credentials(email, password)
        self._raised_ban_user(user)
        self._raise_unverified_email(user)
        
        tokens = AccessandRefreshToken(user).generate()
        return {
            'email': user.email,
            'username': user.username,
            'tokens':{
                'access': tokens.access,
                'refresh': tokens.refresh
            }
        }    
    
    def _raise_invalid_credentials(self, email, password):
        """
        as auth.authenticate(**creds) --> Null for BANNED user and INVALID CREDENTIALS 
        to filter out invalid creds, you need to verify that email or password are wrong
        """
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.check_password(password):
                return None
        raise exceptions.AuthenticationFailed('Invalids Credentials')

    def _raised_ban_user(self, user):
        if not user:
            raise exceptions.AuthenticationFailed("Your account have been ban, please contact an admin")

    def _raise_unverified_email(self, user):
        if not user.email_verified:
            raise exceptions.AuthenticationFailed("Confirm your email first")


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ('email',)



class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ('new_password', 'token', 'uidb64')
    
    def validate(self, attrs):
        new_password = attrs.get('new_password','')
        token = attrs.get('token','')
        uidb64 = attrs.get('uidb64','')

        id = decode_base64(uidb64)

        if not User.objects.filter(id=id).exists():
            raise AuthenticationFailed('Invalids Id')

        user = User.objects.get(id=id)
        if not user.is_password_reset_token_valid(token):
            raise PermissionDenied({"link": "Le lien de réinitialisation n'est pas valide"})
        if user.is_password_same_has_old(new_password):
            raise PermissionDenied({"password": 'Vous avez déjà utilisé ce mot de passe'})


        return {
                'new_password': new_password, 
                'token': token,
                'uidb64': uidb64,
            }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {'token_error': ('Le token est expiré ou invalide')}

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def blacklist_token(self):
        try:
            RefreshToken.blacklist(self.token)
        except TokenError:
            self.fail('token_error')