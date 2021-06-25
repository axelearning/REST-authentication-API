from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('email-verify/request', views.RequestEmailVerificationAPI.as_view(), name='email-verify-request'),
    path('email-verify/confirm', views.ConfirmEmailAPI.as_view(), name='email-verify-confirm'),
    path('login/', views.LoginAPI.as_view(), name='login'),
    path('logout/', views.LogoutAPI.as_view(), name='logout'),
    path('password-reset/request', views.RequestResetPasswordAPI.as_view(), name='password-reset-request'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CheckPasswordTokenAPI.as_view(), name='password-reset-confirm'),
    path('password-reset/complete', views.SetNewPasswordAPI.as_view(), name='password-reset-complete'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
