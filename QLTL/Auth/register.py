
from django.contrib.auth import authenticate
import os
import random
from rest_framework_simplejwt.tokens import RefreshToken

from Auth.models import User

def check_verified(user):
     return user.is_verified
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def generate_username(name):
    print('tao user name')
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)
                            

def register_social_user(provider, user_id, email, username):
    try:
        user_by_email = User.objects.get(email=email)
        print('exists')
        if provider == user_by_email.auth_provider:
                print('same provider')
                registered_user = authenticate(
                    email=email, password=os.environ.get('SOCIAL_SECRET'))
                if not check_verified(registered_user): return {'status':'fail','mess':'Account not verified'}
                token = get_tokens_for_user(registered_user)
                return {
                    'username': registered_user.username,
                    'email': registered_user.email,                                         
                    'tokens': token}
        else:
                print('different provider')
                if not check_verified(user_by_email): return {'status':'fail','mess':'Account not verified'}
                print(check_verified(user_by_email))
                token = get_tokens_for_user(user_by_email)
                return {
                    'username': user_by_email.username,
                    'email': user_by_email.email,                                         
                    'tokens': token}
    except:
        print('tao moi email',email)
        user = {
            'username': generate_username(username), 
            'email': email,
            'password': os.environ.get('SOCIAL_SECRET')}
        print('user',user)
        userCreated = User.objects.create_user(**user)
        print('qua')
        print('user',userCreated)
        userCreated.is_verified = True
        userCreated.auth_provider = provider
        userCreated.save()

        new_user = authenticate(
            email=email, password=os.environ.get('SOCIAL_SECRET'))
        print('tạo tài khoản thành công: ',new_user)
        token =  RefreshToken.for_user(new_user)
        print('token: ',token)
        return {
            'email': new_user.email,
            'username': new_user.username,
            'tokens': token
        }
