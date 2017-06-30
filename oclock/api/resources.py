'''
Created on 17-06-2014

@author: carriagadad
'''

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
#from tastypie.authentication import BasicAuthentication
#from tastypie.authorization import DjangoAuthorization
from tastypie import fields
from oclock.apps.db.models import Users
from tastypie.serializers import Serializer
from oclock.api.models import UserType

class User_Add(ModelResource):
    class Meta:
        resource_name = 'user/get'
        #fields = ['users_name','users_lastname','users_firstname','users_email']
        fields = ['users_type_nombre']
        authentication = Authentication()
        authorization = Authorization()
        #authentication = BasicAuthentication()
        #authorization = DjangoAuthorization()
        queryset = UserType.objects.all()
        allowed_methods = ['get']
        #excludes = ['users_password','fk_users_type','users_delete']
        #serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])
        serializer = Serializer(formats=['json'])
        include_resource_uri = False
        
    #def dehydrate_user_name(self, bundle):
        #return bundle.data['user_name'].upper()
    
    #def dehydrate(self, bundle):
        #bundle.data['users_firstname'] = bundle.obj.users_firstname()
        #return bundle