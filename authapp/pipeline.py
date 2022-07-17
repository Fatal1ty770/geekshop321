from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse
import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden
from authapp.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return

    api_url = urlunparse(('https','api.vk.com','/method/users.get',None, urlencode(OrderedDict(fields=','.join(('bdate', 'sex','about')),access_token=response['access_token'],v='5.92')),None))
    vk_response = requests.get(api_url)

    if vk_response.status_code != 200:
        return

    vk_data = vk_response.json()['response'][0]

    if vk_data['sex']:
        if vk_data['sex'] == 2:
            user.shopuserprofile.gender = ShopUserProfile.MALE
    elif vk_data['sex'] == 1:
        user.shopuserprofile.gender = ShopUserProfile.FEMALE


    if vk_data['about']:
        user.shopuserprofile.aboutMe = vk_data['about']

    if vk_data['bdate']:
        bdate = datetime.strptime(vk_data['bdate'], '%d.%m.%Y').date()
        age = timezone.now().date().year - bdate.year
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.vk.VKOAuth2')
        user.age = age

    user.save()

