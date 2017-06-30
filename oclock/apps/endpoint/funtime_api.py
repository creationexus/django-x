'''
Created on 06-06-2014

@author: carriagadad
'''

"""Clocks API implemented using Google Cloud Endpoints."""

from oclock.apps.base.models import UsersType
from oclock.apps.base.models import Users
from models import *

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from oclock.apps.endpoint import services
from django.conf import settings

# Create the response string
class WebResponse(messages.Message):
    response = messages.StringField(1, required=True)

"""class ValidUser(messages.Message):
    hash = messages.StringField(1, required=True)"""
    
package = 'Api'

"""allowed_client_ids=[settings.GOOGLE_OAUTH2_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID],
scopes=[endpoints.EMAIL_SCOPE, ]
audiences=[ANDROID_AUDIENCE]"""

@endpoints.api(name='funtime', version='v1',
allowed_client_ids=[settings.WEB_CLIENT_ID, settings.ANDROID_CLIENT_ID,
settings.IOS_CLIENT_ID],
audiences=[settings.ANDROID_AUDIENCE]
)
class FunTimeApi(remote.Service):
    """Clocks API v1."""
    
    """PUBLICATION_YEAR_RESOURCE = endpoints.ResourceContainer(
        message_types.VoidMessage,
        year=messages.IntegerField(1, variant=messages.Variant.INT32))

    @endpoints.method(PUBLICATION_YEAR_RESOURCE, ClockCollection,
                      path='list', http_method='GET',
                      name='books.list')
    def book_list(self, request):
        pass"""
        #if hasattr(request, 'year'):
        #    clock_list = Clock.objects.filter(publication_year__year=request.year)
        #else:
        #    clock_list = Clock.objects.all()

        #books = services.ApiUtils.serialize_books(clock_list)
        #return ClockCollection(books=books)

    @endpoints.method(UserLogin, UserLoginResponse, path='user/login/', http_method='POST', name='user.login')
    def user_login(self, request):
        try:
            u_obj = Users.objects.get(users_email=request.users_email)
        except Users.DoesNotExist:
            raise endpoints.NotFoundException('User %s not found.' % (request.users_email,))
        else:
            if u_obj.users_password == request.users_password:
                return UserLoginResponse(
                    hash='yT62Gv8',
                    id=str(u_obj.users_id))
            else:
                raise endpoints.UnauthorizedException('User %s access denied.' % (request.users_email,))
            
    """ID_RESOURCE = endpoints.ResourceContainer(message_types.VoidMessage,
        id=messages.StringField(1, variant=messages.Variant.STRING))"""

    @endpoints.method(GetUser, User, path='user/get/', http_method='POST', name='user.get')
    def user_get(self, request):
        try:
            u_obj = Users.objects.get(users_id=request.id)
        except Users.DoesNotExist:
            raise endpoints.NotFoundException('User %s not found.' % (request.id))
            """return User(users_name='',
            users_lastname='',
            users_firstname='',
            users_email='',
            users_password='',
            users_path_local_avatar='',
            users_path_web_avatar='',
            users_time_zone='',
            users_birthday='',
            users_sex='')"""
        else:
            if(request.hash == 'yT62Gv8'):
                return User(users_name=u_obj.users_name,
                users_lastname=u_obj.users_lastname,
                users_firstname=u_obj.users_firstname,
                users_email=u_obj.users_email,
                users_password=u_obj.users_password,
                users_path_local_avatar=u_obj.users_path_local_avatar,
                users_path_web_avatar=u_obj.users_path_web_avatar,
                users_time_zone=u_obj.users_time_zone,
                users_birthday=str(u_obj.users_birthday),
                users_sex=u_obj.users_sex)
            else:
                raise endpoints.UnauthorizedException('Request denied for user id %s.' % (request.id,))
            """return WebResponse(response='tu n %s ' % str(request.id))"""
            #except (IndexError, TypeError):
            #raise endpoints.NotFoundException('User %s not found.' % (request.id,))

    @endpoints.method(User, WebResponse, path='user/add/', http_method='POST', name='user.add')
    def user_add(self, request):
        try:
            u_obj = Users.objects.get(users_name=request.users_name, users_email=request.users_email)
        except Users.DoesNotExist:
            u = Users(
                users_name=request.users_name,
                users_lastname=request.users_lastname,
                users_firstname=request.users_firstname,
                users_email=request.users_email,
                users_password=request.users_password,
                users_path_local_avatar=request.users_path_local_avatar,
                users_path_web_avatar=request.users_path_web_avatar,
                users_time_zone=request.users_time_zone,
                users_birthday=str(request.users_birthday),
                users_sex=request.users_sex,
                fk_users_type=UsersType.objects.get(users_type_id=1),
                users_delete=0
            )
            u.save()
            u = Users.objects.get(users_email=request.users_email)
            return WebResponse(response='id %s'%str(u.users_id))
        else:
            raise endpoints.BadRequestException('eMail %s exist!' % (request.users_email,))
    
    """@endpoints.method(ValidUser, WebResponse, path='user/checklogin/', http_method='POST', name='user.checklogin')
    def user_checklogin(self, request):
        return WebResponse(response=request.hash)"""
    
"""USER_INFO = endpoints.ResourceContainer(
    #message_types.VoidMessage,
    User,
        users_name=messages.StringField(1, variant=messages.Variant.STRING, required=True),
        users_lastname=messages.StringField(2, variant=messages.Variant.STRING, required=True),
        users_firstname=messages.StringField(3, variant=messages.Variant.STRING, required=True),
        users_email=messages.StringField(4, variant=messages.Variant.STRING, required=True),
        users_password=messages.StringField(5, variant=messages.Variant.STRING, required=True),
        users_path_local_avatar=messages.StringField(6, variant=messages.Variant.STRING, required=True),
        users_path_web_avatar=messages.StringField(7, variant=messages.Variant.STRING, required=True),
        users_time_zone=messages.StringField(8, variant=messages.Variant.STRING, required=True),
        users_birthday=messages.StringField(9, variant=messages.Variant.STRING, required=True),
        users_sex=messages.StringField(10, variant=messages.Variant.STRING, required=True),
    )
    @endpoints.method(USER_INFO, User,
                      path='add/user/{users_name}', http_method='POST',
                      name='users.add')
    def users_add(self, request):
        return User(message='hello %s' % ('ok'))"""