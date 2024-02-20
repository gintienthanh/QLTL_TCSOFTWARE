from rest_framework.response import Response
from rest_framework import status,permissions,serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from Auth.services import google_validate_id_token, user_get_or_create
from django.template.loader import render_to_string
import secrets
import string
import json
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from allauth.socialaccount.models import SocialAccount, SocialApp

from django.contrib.auth.models import User
from Auth.serializers import FacebookSocialAuthSerializer,UserRegistrationSerializer,UserLoginSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer,LogoutSerializer,UserSerializer
from Auth.renderers import UserRenderer
from .utils import Util


class UserRegistrationView(APIView):
    # permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user_data = serializer.data
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(characters) for _ in range(12))
            password_json = json.dumps(password)
            user.set_password(password_json)
            user.save() 
            context = {'password':password}
            html_message = render_to_string('Inform_password.html', context )
            data = {'body': html_message, 'to_email': user.email,
                    'subject': 'Password to login'}
            Util.send_email(data)
            return Response(user_data, status=status.HTTP_201_CREATED)
        except: 
            return Response({'errors':{'non_field_errors':['Error when create user']}}, status=status.HTTP_400_BAD_REQUEST)
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('username')
        password = serializer.data.get('password')
        user = User.objects.get(email=email)
        is_True = check_password(password, user.password)
        if is_True is False:
            return Response({'message: ':'Password not match','status':'400'}, status=status.HTTP_400_BAD_REQUEST)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            if user.is_active is False: return Response({'message: ':'Account unable','status':'400'}, status=status.HTTP_400_BAD_REQUEST)
            if user.last_login is None:
                return Response({
                    'status':403,
                    'mess':'FirstTime Login',
                    'access': str(refresh.access_token),
                    }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        user.last_login = timezone.now()
        return Response({
            'status':200,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'name':user.username,
            'is_admin': user.is_superuser,
            'message':'Login Success'}, status=status.HTTP_200_OK)
        
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
        id = serializers.IntegerField(required=False, default='')
        email = serializers.EmailField()
        username = serializers.CharField(required=False, default='')
        

    def post(self, request, *args, **kwargs):
        id_token = request.headers.get('Authorization')
        google_validate_id_token(id_token=id_token)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'email':serializer.validated_data['email'],
            'username':serializer.validated_data['username']
        }
        user, _ = user_get_or_create(**data)
        uid = serializer.validated_data['id']
        provider = 'google' 
        social_app = SocialApp.objects.get(provider=provider)
        social_account, created = SocialAccount.objects.get_or_create(
            user=user,
            provider=provider,
            uid=uid
        )
        if created:
            social_account.extra_data = {} 
            social_account.app = social_app
            social_account.save()
        user.last_login = timezone.now()
        user.save()
        refresh_token = RefreshToken.for_user(user)
        response = {
            'status':200,
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
            'is_admin': user.is_superuser
        }
        return Response(response,status=status.HTTP_200_OK)
    
class FacebookSocialAuthView(APIView):
    serializer_class = FacebookSocialAuthSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = ((serializer.validated_data)['auth_token'])
        user.last_login = timezone.now()
        user.save()
        refresh_token = RefreshToken.for_user(user)
        response = {
            'status':200,
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
            'is_admin': user.is_superuser
        }
        return Response(response,status=status.HTTP_200_OK)

