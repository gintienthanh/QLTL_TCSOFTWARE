import requests

import facebook
from django.core.exceptions import ValidationError
from decouple import config

from Auth.models import User

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

@staticmethod
def facebookValidate(auth_token):
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=name,email')
            return profile
        except:
            return "The token is invalid or expired."
def google_validate_id_token(*, id_token: str) -> bool:
    # Reference: https://developers.google.com/identity/sign-in/web/backend-auth#verify-the-integrity-of-the-id-token
    response = requests.get(
        GOOGLE_ID_TOKEN_INFO_URL,
        params={'id_token': id_token}
    )

    if not response.ok:
        raise ValidationError('id_token is invalid.')

    audience = response.json()['aud']

    if audience != config('GOOGLE_CLIENT_ID'):
        raise ValidationError('Invalid audience.')

    return True


# def google_get_access_token(*, code: str, redirect_uri: str) -> str:
#     # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
#     data = {
#         'code': code,
#         'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
#         'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
#         'redirect_uri': redirect_uri,
#         'grant_type': 'authorization_code'
#     }
#     print('data: ',data)
#     print('GOOGLE_ACCESS_TOKEN_OBTAIN_URL: ',GOOGLE_ACCESS_TOKEN_OBTAIN_URL)
#     response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
#     print('response: ',response.text)
#     if not response.ok:
#         raise ValidationError('Failed to obtain access token from Google.')

#     access_token = response.json()['access_token']

#     return access_token


# def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
#     # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
#     response = requests.get(
#         GOOGLE_USER_INFO_URL,
#         params={'access_token': access_token}
#     )

#     if not response.ok:
#         raise ValidationError('Failed to obtain user info from Google.')

#     return response.json()
# @transaction.atomic
# def user_get_or_create(*, email: str, **extra_data) -> Tuple[User, bool]:
#     user = User.objects.filter(email=email).first()

#     if user:
#         return user, False

#     return user_create(email=email, **extra_data), True
# def user_create(email, password=None, **extra_fields) -> User:
#     extra_fields = {
#         'is_admin': False,
#         'is_verified':True,
#         **extra_fields
#     }

    # user = User(email=email, **extra_fields)

    # if password:
    #     user.set_password(password)
    # else:
    #     user.set_unusable_password()

    # user.full_clean()
    # user.save()

    # return user