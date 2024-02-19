
from django.contrib.auth import authenticate
import os
import random
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User

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
                            

def register_social_user(provider, email, username, user_id =None):
    # case find user success
    try:
        user_by_email = User.objects.get(email=email)
        # case same provider
        if provider == user_by_email.auth_provider:
                registered_user = authenticate(
                    email=email, password=os.environ.get('SOCIAL_SECRET'))
                if not check_verified(registered_user): return {'status':'fail','mess':'Account not verified'}
                refresh = RefreshToken.for_user(registered_user)
                return {
                    'id':registered_user.id,
                    'username': registered_user.username,
                    'email': registered_user.email,                                         
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)}
        # case difference provider
        else:
                if not check_verified(user_by_email): return {'status':'fail','mess':'Account not verified'}
                refresh = RefreshToken.for_user(user_by_email)
                return {
                     'id':user_by_email.id,
                    'username': user_by_email.username,
                    'email': user_by_email.email,                                         
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)}
    # catch find user fail there by create new user
    except:
        user = {
            'username': generate_username(username), 
            'email': email,
            'password': os.environ.get('SOCIAL_SECRET')}
        userCreated = User.objects.create_user(**user)
        userCreated.is_verified = True
        userCreated.auth_provider = provider
        userCreated.save()

        new_user = authenticate(
            email=email, password=os.environ.get('SOCIAL_SECRET'))
        refresh =  RefreshToken.for_user(new_user)
        return {
            'id':new_user.id,
            'email': new_user.email,
            'username': new_user.username,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
