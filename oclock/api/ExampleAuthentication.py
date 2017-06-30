'''
Created on 23-06-2014

@author: carriagadad
'''

from oclock.apps.db.models import Users
from rest_framework import authentication
from rest_framework import exceptions

class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('X_USERNAME')
        if not username:
            return 1
        try:
            user = Users.objects.get(users_name=username)
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        return (user, 1)