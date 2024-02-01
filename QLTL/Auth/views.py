from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status,permissions,serializers
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from datetime import datetime
from Auth.services import google_validate_id_token
from .register import register_social_user
from django.template.loader import render_to_string
import secrets
import string


from Auth.models import User
from Auth.serializers import FacebookSocialAuthSerializer,UserRegistrationSerializer,UserLoginSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer,LogoutSerializer,UserSerializer
from Auth.renderers import UserRenderer
from .utils import Util

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
        email = serializers.EmailField()
        first_name = serializers.CharField(required=False, default='')
        last_name = serializers.CharField(required=False, default='')

    def post(self, request, *args, **kwargs):
        id_token = request.headers.get('Authorization')
        google_validate_id_token(id_token=id_token)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        first_name = str(serializer.data.get('first_name'))
        last_name = str(serializer.data.get('last_name'))
        register_social_user(
            provider='google',
            email=serializer.data.get('email'),
            username= first_name + last_name,
        )
        user = User.objects.get(email = serializer.data.get('email'))
        user.last_login(datetime.now())
        user.save()
        refresh_token = RefreshToken.for_user(user)
        response = {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        }
        return Response(response,status=status.HTTP_200_OK)
    
class FacebookSocialAuthView(APIView):
    serializer_class = FacebookSocialAuthSerializer
    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        print('response:',data)
        return Response({'data':data}, status=status.HTTP_200_OK)

