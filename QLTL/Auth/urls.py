from django.urls import path
from Auth.views import UnLockAccountView,LockAccountView,GoogleLoginApi,FacebookSocialAuthView,UserRegistrationView,UserLoginView,UserChangePasswordView,SendPasswordResetEmailView,UserPasswordResetView,LogoutAPIView
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

urlpatterns = [
    ##api
    path('register/',UserRegistrationView.as_view(),name="register"),
    path('login/',UserLoginView.as_view(),name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('lock-account/', LockAccountView.as_view(), name='lock-account'),
    path('unlock-account/', UnLockAccountView.as_view(), name='unlock-account'),
    # oauth
    path('oauth/google/', GoogleLoginApi.as_view(), name="google"),
    path('oauth/facebook/', FacebookSocialAuthView.as_view(), name="facebook"),
]