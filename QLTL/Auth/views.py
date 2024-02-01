from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status,permissions,serializers
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from datetime import datetime
from django.shortcuts import redirect
from urllib.parse import urlencode
from django.template.loader import render_to_string
import secrets
import string
import os
# from dotenv import load_dotenv
# load_dotenv()

from Auth.models import User
from Auth.serializers import FacebookSocialAuthSerializer,UserRegistrationSerializer,UserLoginSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer,LogoutSerializer,UserSerializer
from Auth.renderers import UserRenderer
from .utils import Util
from Auth.services import user_get_or_create
from Auth.services import  google_get_access_token, google_get_user_info

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
class UserRegistrationView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = serializer.data
       
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(12))
        user.set_password(password)
        user.save()
        context = {'password':password}
        html_message = render_to_string('Inform_password.html', context )
        data = {'body': html_message, 'to_email': user.email,
                'subject': 'Verify your email'}
        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email,password=password)
        if user is not None:
            if not user.is_active:
                raise AuthenticationFailed('Account disabled, contact admin')
            token = get_tokens_for_user(user)
            if user.last_login is None:
                return Response({'mess':'FirstTime Login','token':token}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        return Response({'token':token,'msg':'Login Success'}, status=status.HTTP_200_OK)
        

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self,request,format = None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)
    
#for to reset password
class SendPasswordResetEmailView(APIView):
    renderer_classes =[UserRenderer]
    def post(self,request,format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset link send. Please check your Email'},status=status.HTTP_200_OK)
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,uid,token,format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)    
class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response('logout!',status=status.HTTP_204_NO_CONTENT)
class GoogleLoginApi( APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        # receive code or error when google call api callback
        # validate them and set url login FE
        # check error with code if have one of them return error page
        # get access token from function google_get_access_token (we need code google_get_access_token to handle)
        # and then use access token to get user info
        # check user have already if have update field lastLogin of user use time now else create new user with profile_data from user info
        # create token for user and redirect Url FE with both token and user info on cookie
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        code = validated_data.get('code')
        
        error = validated_data.get('error')

        login_url = 'http://localhost:3000/login'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        domain = os.environ.get('BASE_BACKEND_URL')
        api_uri = 'oauth/google/'
        redirect_uri = f'{domain}{api_uri}'
        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        user_data = google_get_user_info(access_token=access_token)

        profile_data = {
            'email': user_data['email'],
            'first_name': user_data.get('givenName', ''),
            'last_name': user_data.get('familyName', ''),
        }
        user, _ = user_get_or_create(**profile_data)
        user.last_login = datetime.now()
        user.auth_provider = 'google'
        user.save()
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        response = redirect(to = os.environ.get('BASE_FRONTEND_URL'))
        serializer = UserSerializer(user)
        response.set_cookie(key='token',value=token)
        response.set_cookie(key='user',value=serializer.data)
        print(serializer)
        return response   
class FacebookSocialAuthView(APIView):
    serializer_class = FacebookSocialAuthSerializer
    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        print('response:',data)
        return Response({'data':data}, status=status.HTTP_200_OK)

