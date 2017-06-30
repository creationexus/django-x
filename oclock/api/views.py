'''
Created on 23-06-2014
@author: carriagadad
'''
from rest_framework.authentication import TokenAuthentication,OAuth2Authentication
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import viewsets,mixins
from rest_framework import views
from oclock.apps.db.models import Users,UsersType,Events,UsersRequestEmail,Hashtags,UsersHasHashtags,NetworksType,SocialNetworks,UsersUnfollowsEvents,EventsLow,EventsMedium,EventsHigh,EventsSpecial
from oclock.apps.db.models import EventsHasHashtags,UsersFollowsEvents,UsersWritesComments,Comments,Zone,Timezone,SharedEvents,UsersHideEvents,Invitations,Activities,EventsInvitations,EventsAfter
from django.db.models import Q
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from oclock.api.serializers import UserSerializer,UserTypeSerializer,EventSerializer,ResetPasswordSerializer,UserRequestEmailSerializer,PaginatedEventSerializer,PaginatedUserSerializer,SharedEventSerializer,PaginatedCommentSerializer,InvitationSerializer
from oclock.api.serializers import HashtagSerializer,UserHasHashtagSerializer,NetworkTypeSerializer,SocialNetworkSerializer,UserFollowEventSerializer,UserWriteCommentSerializer,UserHideEventSerializer,CommentSerializer,PaginatedUserWriteCommentSerializer,EventSpecialSerializer
from . import negotiators, parsers
from rest_framework import status
from django.shortcuts import get_object_or_404
from provider.oauth2.models import Client
from oclock.apps.mailing.services import Mandrill_Services
from django.template import RequestContext,loader
import hashlib
import random
import time
import urllib
import cgi
import json
from rest_framework import permissions
from django.http import HttpResponse
import cloudstorage as gcs
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from django.conf import settings
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
from provider.oauth2.models import Client
import urllib2
from provider.oauth2.models import AccessToken
from dateutil.parser import parse as parse_datetime
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from datetime import timedelta,datetime
from dateutil import tz
from pubnub.Pubnub import Pubnub
from django.db.models import Count
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import images
import unicodedata,re
from django.core import serializers
from django.views.decorators.cache import cache_page
from mixpanel import Mixpanel
from django.core.files.base import ContentFile
from google.appengine.api import rdbms
from google.appengine.api import urlfetch
from oclock.apps.media.images import init_image
from oclock.apps.db.datastore import EventsQueue
import logging
def notifsocket():
    return Pubnub('pub-c-4a7ce3d0-bcc6-4f50-94aa-5cf469d6182e','sub-c-56c8ca56-a255-11e4-8d46-02ee2ddab7fe','sec-c-OTc3NTZjY2QtMmMyOS00MTg4LWI3ZDAtZDk5MTc4NTA4OTg5',True)
def mysqlconn():
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    return rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
def getUserIdByToken(key):
    if not key:
        return Response({'Error':'No token provided.'},status=status.HTTP_401_UNAUTHORIZED)
    else:
        try:
            token=AccessToken.objects.get(token=key.replace("Bearer","").strip())
            if not token:
                return Response({'Error':'Access denied.'},status=status.HTTP_401_UNAUTHORIZED)
            if token.expires<datetime.now():
                return Response({'Error':'Token has expired.'},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return token.user_id
        except AccessToken.DoesNotExist,e:
            return Response({'Error':'Access denied.'},status=status.HTTP_401_UNAUTHORIZED)
def inet_aton(addr):
    addr = addr.split('.')
    num = int(addr[0]) << 24 | int(addr[1]) << 16 | int(addr[2]) << 8 | int(addr[3])
    return num
def getCountryByIP(ip,ip_attr):
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
    c=conn.cursor()
    if ip_attr is not None and ip_attr.strip()!='':
        ip=ip_attr
    c.execute('SELECT cc FROM geoip_country WHERE INET_ATON(%s) BETWEEN start AND end LIMIT 1',(ip,))
    #c.execute('SELECT cc FROM geoip_country WHERE %s BETWEEN start AND end LIMIT 1',(inet_aton(ip),))
    val=c.fetchone()
    if val is None:
        return None
    c.close()
    conn.close()
    return val[0]
def notifAll(e_id,u_id,action):
    #user_id
    #user_action_id
    #action=3,
    #object
    #activities_date=datetime.now()
    conn=mysqlconn()
    c=conn.cursor()
    creator=0
    #creator
    c.execute('SELECT fk_user_creator FROM events e WHERE events_id=%s',(e_id,))
    for orq in c.fetchall():
        creator=orq[0]
        Activities(user_id=orq[0],user_action_id=u_id,action=action,object=e_id,activities_date=datetime.now()).save(force_insert=True)
    #follow and comment
    pubnub=notifsocket()
    c.execute('SELECT u.users_id FROM users u LEFT JOIN events e ON e.fk_user_creator=u.users_id WHERE u.users_id IN(SELECT ufe.fk_users FROM users_follows_events ufe WHERE ufe.fk_events=%s) OR u.users_id IN(SELECT uwc.fk_users FROM users_writes_comments uwc WHERE uwc.fk_events=%s AND uwc.users_writes_comments_delete=0) GROUP BY u.users_id',(e_id,e_id))
    for orq in c.fetchall():
        if creator==orq[0]:
            continue
        else:
            pubnub.publish({
                'channel':'userch_'+str(orq[0]),
                'message':{'user_id':str(orq[0])}
            })
            Activities(user_id=orq[0],user_action_id=u_id,action=(action+1),object=e_id,activities_date=datetime.now()).save(force_insert=True)
    c.close()
    conn.close()
class CreateUserViewSet(viewsets.ModelViewSet):
    queryset=Users.objects.filter(users_id=0)
    serializer_class = UserSerializer
    def create(self,request,*args,**kwargs):
        #upload_url = blobstore.create_upload_url('/upload')
        #serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        serializer = self.get_serializer(data=request.DATA)
        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            if serializer.is_valid():
                try:
                    #|  2 |       1 | web     | https://festive-ally-585.appspot.com/ | https://festive-ally-585.appspot.com/ | 02770b9b0452d7e56a1d | 0b671033626580921b56593440c3e387d0cb5ec6 |           0 |
                    #|  3 |       1 | android | https://festive-ally-585.appspot.com/ | https://festive-ally-585.appspot.com/ | a3011c8a95a1bef99a3a | 98bb44de40a7852ea6ca61977ee8e811f935745d |           1 |
                    serializer.object.users_delete = 0
                    serializer.object.fk_users_type = UsersType.objects.get(users_type_id=1)
                    #serializer.object.users_password=hashlib.sha1(str(serializer.object.users_password)).hexdigest()
                    self.pre_save(serializer.object)
                    self.object = serializer.save(force_insert=True)
                    #self.object.save()
                    self.post_save(self.object, created=True)
                    headers = self.get_success_headers(serializer.data)
                    u = Users.objects.get(users_email=serializer.object.users_email)
                    serializer.data.users_id=u.users_id
                    c=Client(user_id=u.users_id,name=u.users_email,url='',redirect_uri='',client_id='02770b9b0452d7e56a1d',client_secret='0b671033626580921b56593440c3e387d0cb5ec6',client_type=1).save()
                    #serializer.object.users_id = Users.objects.get(users_email=serializer.data.users_email)
                    return Response({'users_id':u.users_id}, status=status.HTTP_201_CREATED, headers=headers)
                except IntegrityError:
                    return Response({'status':'email exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request):
        users_name=self.request.QUERY_PARAMS.get('users_name',None)
        users_name_id=self.request.QUERY_PARAMS.get('users_name_id',None)
        queryset=Users.objects.filter(users_id=0)
        if users_name is not None and users_name.strip() != '':
            queryset=Users.objects.filter(users_name__icontains=str(users_name))
        if users_name_id is not None and users_name_id.strip() != '':
            queryset=Users.objects.filter(users_name_id__icontains=str(users_name_id))
        queryset=queryset.order_by('users_name')
        if False:
            paginator = Paginator(queryset,10)
            page = request.QUERY_PARAMS.get('page')
            try:
                users=paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                users=paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999),
                # deliver last page of results.
                users=paginator.page(paginator.num_pages)
            serializer_context = {'request': request}
            serializer = PaginatedUserSerializer(users,context=serializer_context)
            return Response(serializer.data)
        else:
            serializer=UserSerializer(queryset,many=True)
            return Response(serializer.data)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class UsersViewSet(viewsets.ModelViewSet):
    queryset=Users.objects.filter(users_id=0)
    serializer_class = UserSerializer
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    def list(self,request):
        users_name=self.request.QUERY_PARAMS.get('users_name',None)
        users_name_id=self.request.QUERY_PARAMS.get('users_name_id',None)
        queryset=Users.objects.filter(users_id=0)
        if users_name is not None and users_name.strip() != '':
            queryset=Users.objects.filter(users_name__icontains=str(users_name))
        if users_name_id is not None and users_name_id.strip() != '':
            queryset=Users.objects.filter(users_name_id__icontains=str(users_name_id))
        queryset=queryset.order_by('users_name')
        if False:
            paginator = Paginator(queryset,10)
            page = request.QUERY_PARAMS.get('page')
            try:
                users=paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                users=paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999),
                # deliver last page of results.
                users=paginator.page(paginator.num_pages)
            serializer_context = {'request': request}
            serializer = PaginatedUserSerializer(users,context=serializer_context)
            return Response(serializer.data)
        else:
            serializer=UserSerializer(queryset,many=True)
            return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def retrieve(self, request, pk=None):
        queryset = Users.objects.all()
        user=get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    def update(self,request,pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        """queryset=Users.objects.all()
        user=get_object_or_404(queryset,pk=pk)
        serializer=UserSerializer(user,data=request.DATA)
        if serializer.is_valid():"""
        """UsersHasHashtags.objects.filter(fk_users=user).delete()
        hashs=serializer.object.users_hashtags.split(',')
        for hash in hashs:
            try:
                hashtag=Hashtags.objects.get(hashtags_value=hash)
            except Hashtags.DoesNotExist:
                hashtag=Hashtags(hashtags_value=hash).save()
                hashtag=Hashtags.objects.get(hashtags_value=hash)
            uhhashtag=UsersHasHashtags(fk_users=user,fk_hashtags=hashtag)
            uhhashtag.save()"""
        """serializer.save()
        return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
    def partial_update(self,request,pk=None):
        key=request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist,e:
                return Response({'Error': 'Token does not exist.'})
        if int(token_user)==int(pk):
            queryset=Users.objects.all()
            user=get_object_or_404(queryset,pk=token_user)
            serializer=UserSerializer(user,data=request.DATA,partial=True)
            if serializer.is_valid():
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        """queryset = Users.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        user.delete()
        serializer = UserSerializer(user)
        return Response(serializer.data)"""
class UsersTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset=UsersType.objects.all()
    serializer_class=UserTypeSerializer
    authentication_classes=(OAuth2Authentication,)
    permission_classes=(IsAuthenticated,)
    #search_fields = ('users_type_nombre')
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):        
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
def slugify(str):
    slug = unicodedata.normalize("NFKD",unicode(str)).encode("ascii","ignore")
    slug = re.sub(r"[^\w]+", " ", slug)
    slug = "-".join(slug.lower().strip().split())
    return slug
class EventViewSet(viewsets.ModelViewSet):
    #authentication_classes=(OAuth2Authentication,)
    #permission_classes=(IsAuthenticated,)
    queryset=Events.objects.order_by('events_id')
    serializer_class=EventSerializer
    parser_classes=(FileUploadParser,)
    #filter_backends = (filters.DjangoFilterBackend,)
    #parser_classes = (MultiPartParser,)
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #filter_fields = ('events_title')
    def create(self,request):
        key=request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token=AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist, e:
                return Response({'Error': 'Token does not exist.'})
        #request.DATA=request.DATA.copy()
        request.DATA['fk_user_creator']='/api/users/%s/'%str(token_user)
        serializer=self.get_serializer(data=request.DATA)
        #serializer = EventSerializer(data=request.DATA, files=request.FILES)
        if serializer.is_valid():
            country=getCountryByIP(request.META.get('REMOTE_ADDR'),serializer.object.events_ip)
            utz=Users.objects.get(users_id=token_user)
            u_zone=0
            n_min=0
            if utz.users_time_zone is not None:
                u_zone=float(utz.users_time_zone)#int(utz.users_time_zone)
            if serializer.object.events_type.strip()!='1' and serializer.object.events_type.strip()!='2':
                return Response({"status":"error in events_type"}, status=status.HTTP_400_BAD_REQUEST)
            elif serializer.object.events_type.strip()=='1' and serializer.object.events_start is not None:
                serializer.object.events_finish=None
                if u_zone>0: 
                    serializer.object.events_start-=timedelta(hours=u_zone)
                else:
                    serializer.object.events_start+=timedelta(hours=u_zone*(-1))
            elif serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                serializer.object.events_start=None
                if u_zone>0:
                    serializer.object.events_finish-=timedelta(hours=u_zone)
                else:
                    serializer.object.events_finish+=timedelta(hours=u_zone*(-1))
            serializer.object.events_tz=u_zone
            if serializer.object.events_type.strip()=='1' and (serializer.object.events_start is None or serializer.object.events_start=='' or serializer.object.events_start>datetime.now()):
                return Response({"status":"error in events_start"}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.object.events_type.strip()=='2' and (serializer.object.events_finish is None or serializer.object.events_finish=='' or serializer.object.events_finish<=datetime.now()):
                return Response({"status":"error in events_finish"}, status=status.HTTP_400_BAD_REQUEST)
            file_name_hash=None
            try:
                imm=request.FILES['events_image']
                file_name_hashs=init_image(imm,0)
                if type(file_name_hashs) is int:
                    return Response({"image":["error %s."%(str(file_name_hash))]},status=status.HTTP_400_BAD_REQUEST)
                file_name_hash=file_name_hashs[0]
                if serializer.object.events_ip is None or serializer.object.events_ip.strip() == '':
                    serializer.object.events_ip=request.META.get('REMOTE_ADDR')
                serializer.object.events_velocity=1000
                serializer.object.events_level=1
                serializer.object.events_delete=0
                serializer.object.events_enable=1
                serializer.object.events_cc=country
                serializer.object.events_sort=0
                serializer.object.events_image_stamp=file_name_hashs[1]
                if serializer.object.events_skins==None or serializer.object.events_skins=="":
                    serializer.object.events_skins="skin1"
                serializer.object.events_image=file_name_hash
                e_title=serializer.object.events_title.replace('-', ' ').strip()
                e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                e_title=slugify(e_title)
                if len(e_title.strip())==0:
                    e_title='oclock';
                #verificar si existe
                n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                if n_title > 0: 
                    serializer.object.events_title_id=e_title+'-'+str(n_title)
                else:
                    serializer.object.events_title_id=e_title
                #serializer.save()
                self.pre_save(serializer.object)
                self.object=serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                
                """if serializer.object.hashtags.strip()=="" or serializer.object.hashtags is None:
                    hashs=serializer.object.events_title.split(' ')
                    for hash in hashs:
                        try:
                            e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                            hashtag=Hashtags.objects.get(hashtags_value=slugify(hash.replace('?', ' ').strip()))
                            try:
                                uhhashtag=EventsHasHashtags.objects.get(fk_events=e,fk_hashtags=hashtag)
                            except EventsHasHashtags.DoesNotExist:
                                uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            pass"""
                            
                hashs=serializer.object.hashtags.split(',')
                i=0
                while i<len(hashs) and i<range(3):
                    hash=hashs[i].replace('?','').replace('#','').strip()
                    #hash=slugify(hash.replace('?','').replace('#','')).strip()
                    #if len(hash)==0:
                    if hash.strip()!="" and len(hash)>0 and len(hash)<=15:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)                        
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value_str=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            hashtag=Hashtags(hashtags_value=hash,hashtags_value_str=hash).save()
                            hashtag=Hashtags.objects.get(hashtags_value_str=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                    i+=1
                headers = self.get_success_headers(serializer.data)
                if serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                    ev=EventsQueue(
                        events_id=str(serializer.data['events_id']),
                        events_title=serializer.data['events_title'],
                        events_title_id=serializer.data['events_title_id'],
                        fk_user_creator=str(serializer.data['fk_users']['users_id']),
                        events_finish=serializer.data['events_finish'],
                        events_alert_minutes=5
                    )
                    ev.put()
                    
                    """n_seg=(serializer.object.events_finish-datetime.now()).total_seconds()
                    n_min=n_seg/60
                    n_dia=n_min/60/24
                    e=Events.objects.filter(events_id=serializer.data['events_id'])
                    if n_min<10:
                        EventsHigh(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_min>=10 and n_min<30:
                        EventsHigh(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_min>=30 and n_dia<1:
                        EventsMedium(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_dia>=1:
                        EventsLow(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()"""
                        
                        
                UsersFollowsEvents(fk_users=utz,fk_events=Events.objects.get(events_id=serializer.data['events_id'])).save(force_insert=True)
                
                return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except MultiValueDictKeyError:
                if serializer.object.events_ip is None or serializer.object.events_ip.strip() == '':
                    serializer.object.events_ip=request.META.get('REMOTE_ADDR')
                serializer.object.events_velocity=1000
                serializer.object.events_level=1
                serializer.object.events_delete=0
                serializer.object.events_enable=1
                serializer.object.events_cc=country
                serializer.object.events_sort=0
                serializer.object.events_image=file_name_hash
                serializer.object.events_image_stamp='https://storage.googleapis.com/oclock-images/default_normal.png'
                if serializer.object.events_img_str.strip()!='':
                    serializer.object.events_image=serializer.object.events_img_str
                if serializer.object.events_skins==None or serializer.object.events_skins=="":
                    serializer.object.events_skins="skin1"
                e_title=serializer.object.events_title.replace('-', ' ').strip()
                e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                e_title=slugify(e_title)
                if len(e_title.strip())==0:
                    e_title='oclock'; 
                n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                if n_title > 0: 
                    serializer.object.events_title_id=e_title+'-'+str(n_title)
                else:
                    serializer.object.events_title_id=e_title
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                
                """if serializer.object.hashtags.strip()=="" or serializer.object.hashtags is None:
                    hashs=serializer.object.events_title.split(' ')
                    for hash in hashs:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                        hash=slugify(hash.replace('?', ' ').strip())
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            #if hashtag is None:
                            #hashtag=Hashtags(hashtags_value=hash).save()
                            #hashtag=Hashtags.objects.get(hashtags_value=hash)
                            pass"""
                hashs=serializer.object.hashtags.split(',')
                i=0
                while i<len(hashs) and i<range(3):
                    hash=hashs[i].replace('?','').replace('#','').strip()
                    #hash=slugify(hash.replace('?','').replace('#','')).strip()
                    #if len(hash)==0:
                    if hash.strip()!="" and len(hash)>0 and len(hash)<=15:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)                        
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value_str=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            hashtag=Hashtags(hashtags_value=hash,hashtags_value_str=hash).save()
                            hashtag=Hashtags.objects.get(hashtags_value_str=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                    i+=1
                headers=self.get_success_headers(serializer.data)
                
                if serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                    
                    ev=EventsQueue(
                        events_id=str(serializer.data['events_id']),
                        events_title=serializer.data['events_title'],
                        events_title_id=serializer.data['events_title_id'],
                        fk_user_creator=str(serializer.data['fk_users']['users_id']),
                        events_finish=serializer.data['events_finish'],
                        events_alert_minutes=5
                    )
                    ev.put()
                    
                    """n_seg=(serializer.object.events_finish-datetime.now()).total_seconds()
                    n_min=n_seg/60
                    n_dia=n_min/60/24
                    e=Events.objects.filter(events_id=serializer.data['events_id'])
                    if n_min<10:
                        EventsHigh(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_min>=10 and n_min<30:
                        EventsHigh(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_min>=30 and n_dia<1:
                        EventsMedium(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()
                    elif n_dia>=1:
                        EventsLow(events_id=serializer.data['events_id'],events_title=serializer.data['events_title'],events_description=serializer.data['events_description'],events_latitude=serializer.data['events_latitude'],events_longitude=serializer.data['events_longitude'],events_start=serializer.data['events_start'],events_finish=serializer.data['events_finish'],events_type=serializer.data['events_type'],fk_user_creator=Users.objects.get(users_id=serializer.data['fk_users']['users_id']),events_enable=1,events_delete=0,events_language=serializer.data['events_language'],events_country=serializer.data['events_country'],events_velocity=serializer.data['events_velocity'],events_image=serializer.data['events_image'],events_level=serializer.data['events_level'],events_title_id=serializer.data['events_title_id'],events_skins=serializer.data['events_skins'],events_fb_event_id=None,events_date_creation=None,hashtags=None).save()"""
                        
                        
                UsersFollowsEvents(fk_users=utz,fk_events=Events.objects.get(events_id=serializer.data['events_id'])).save(force_insert=True)
                return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self,request):
        events_title_id = self.request.QUERY_PARAMS.get('events_title_id',None)
        events_title=self.request.QUERY_PARAMS.get('events_title',None)
        me=self.request.QUERY_PARAMS.get('me',None)
        new=self.request.QUERY_PARAMS.get('new',None)
        hot=self.request.QUERY_PARAMS.get('hot',None)
        queryset=Events.objects.all()
        if events_title_id is not None:
            queryset=Events.objects.filter(events_title_id=str(events_title_id))
        if events_title is not None and events_title.strip() != '':
            queryset=Events.objects.filter(events_title__icontains=str(events_title))
            queryset=queryset.order_by('-events_date_creation')
        if me is not None:
            key=self.request.META.get('HTTP_AUTHORIZATION')
            if not key:
                return Response({'Error':'No token provided.'})
            else:
                try:
                    token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                    if not token:
                        return Response({'Error':'Access denied.'})
                    if token.expires<datetime.now():
                        return Response({'Error':'Token has expired.'})
                    else:
                        token_user=token.user_id
                except AccessToken.DoesNotExist, e:
                    return Response({'Error': 'Token does not exist.'})
            ufe=UsersFollowsEvents.objects.filter(fk_users=token_user)
            str_where=''
            for uuu in ufe:
                str_where+=str(uuu.fk_events.events_id)+","
            if len(str_where) <= 0:
                queryset=Events.objects.extra(where=["fk_user_creator="+str(token_user)])
            else:
                queryset=Events.objects.extra(where=["fk_user_creator="+str(token_user)+" or events_id in ("+str_where[:-1]+")"])
            queryset=queryset.order_by('-events_id')
        if new is not None:
            queryset=Events.objects.all().order_by('-events_id')
        if hot is not None:
            key=self.request.META.get('HTTP_AUTHORIZATION')
            if not key:
                return Response({'Error':'No token provided.'})
            else:
                try:
                    token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                    if not token:
                        return Response({'Error':'Access denied.'})
                    if token.expires < datetime.now():
                        return Response({'Error':'Token has expired.'})
                    else:
                        token_user=token.user_id
                except AccessToken.DoesNotExist, e:
                    return Response({'Error': 'Token does not exist.'})
            queryset=list(Events.objects.raw('select e.* from events e left join users_follows_events ufe on ufe.fk_events=e.events_id group by e.events_id order by count(*) desc'))
        if events_title_id is None:
            paginator=Paginator(queryset,10)
            page=request.QUERY_PARAMS.get('page')
            try:
                events=paginator.page(page)
            except PageNotAnInteger:
                events=paginator.page(1)
            except EmptyPage:
                events=paginator.page(paginator.num_pages)
            serializer_context={'request':request}
            serializer=PaginatedEventSerializer(events,context=serializer_context)
            return Response(serializer.data)
        else:
            serializer_context={'request':request}
            serializer=EventSerializer(queryset,many=True)
            return Response(serializer.data)
    def retrieve(self, request, pk=None):
        queryset=Events.objects.all()
        event=get_object_or_404(queryset, pk=pk)
        serializer=EventSerializer(event)
        serializer.data.events_seconds=1000
        return Response(serializer.data)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self,request,pk=None):
        key=request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'},status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                token=AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'},status=status.HTTP_401_UNAUTHORIZED)
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist, e:
                return Response({'Error': 'Token does not exist.'},status=status.HTTP_401_UNAUTHORIZED)
            queryset=Events.objects.all()
            event=get_object_or_404(queryset,pk=pk)
            if event.fk_user_creator.users_id==token_user:
                event.events_delete=1
                event.save()
                #ELIMINAR DE LAS LISTAS DE PRIORIDADES
                #serializer=EventSerializer(event)
                """EventsLow.objects.filter(events_id=pk).delete()
                EventsMedium.objects.filter(events_id=pk).delete()
                EventsHigh.objects.filter(events_id=pk).delete()"""
                ev=EventsQueue.query(EventsQueue.events_id==str(pk)).get()
                if ev is not None:
                    ev.key.delete()
                return Response({'events_id':pk},status=status.HTTP_200_OK)
            else:
                return Response('',status=status.HTTP_401_UNAUTHORIZED)
        return Response('',status=status.HTTP_401_UNAUTHORIZED)
class ResetPasswordViewSet(viewsets.ModelViewSet):
    serializer_class = ResetPasswordSerializer
    queryset = Users.objects.all()
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            user = Users.objects.filter(users_email=serializer.object.users_email)[:1]
            if user.count()>0:
                ms=Mandrill_Services()
                url_hash=hashlib.sha1(str(random.uniform(1, 999999))+str(time.time())).hexdigest()
                request_email=UsersRequestEmail(fk_users=user[0],users_request_email_hash=url_hash,users_request_email_enable=1)
                request_email.save()
                #template_values = {'hash': hashlib.sha1(str(random.uniform(1, 999999))).hexdigest()[8:16]}
                template_values = {'hash':url_hash}
                t=loader.get_template('oclock/mail/request_password.html')
                c=RequestContext(request, template_values)
                html=t.render(c)
                if ms.send_mail(serializer.object.users_email,'Request confirmation',html)>0:
                    return Response({'status':'SENT'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'status':'ERROR'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status':'Usuario no existe'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            queryset = UsersRequestEmail.objects.all()
            user_request_email = get_object_or_404(queryset,users_request_email_hash=pk)
            if user_request_email.users_request_email_enable > 0:
                ms = Mandrill_Services()
                pass_hash=hashlib.sha1(str(random.uniform(1, 999999))+str(time.time())).hexdigest()[8:16]
                u=user_request_email.fk_users;
                #actualizar clave usuario
                u.users_password=hashlib.sha1(str(pass_hash)).hexdigest()
                u.save()
                #actualizar estado de hash
                user_request_email.users_request_email_enable=0
                user_request_email.save()
                template_values = {'hash':pass_hash}
                t = loader.get_template('oclock/mail/new_password.html')
                c = RequestContext(request, template_values)
                html = t.render(c)
                if ms.send_mail(u.users_email,'Your new password!',html) > 0:
                    return Response({'status':'SENT'},status=status.HTTP_200_OK)
                else:
                    return Response({'status':'ERROR'})
            else:
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class HashtagsViewSet(viewsets.ModelViewSet):
    serializer_class=HashtagSerializer
    queryset=Hashtags.objects.order_by('hashtags_value')
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        queryset = Hashtags.objects.all()
        usertype = get_object_or_404(queryset, pk=pk)
        serializer = HashtagSerializer(usertype)
        return Response(serializer.data)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class UsersHasHashtagsViewSet(viewsets.ModelViewSet):
    serializer_class=UserHasHashtagSerializer
    queryset = UsersHasHashtags.objects.order_by('users_has_hashtags_id')
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        queryset = UsersHasHashtags.objects.all()
        usertype = get_object_or_404(queryset, pk=pk)
        serializer = UserHasHashtagSerializer(usertype)
        return Response(serializer.data)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class NetworksTypeViewSet(viewsets.ModelViewSet):
    serializer_class=NetworkTypeSerializer
    queryset=NetworksType.objects.order_by('networks_type_id')
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
"""def _get_user_by_email(email):
    try:
        return Users.objects.get(users_email=email)
    except Users.DoesNotExist:
        return None"""
class SocialNetworksViewSet(viewsets.ModelViewSet):
    serializer_class=SocialNetworkSerializer
    queryset=SocialNetworks.objects.order_by('social_networks_id')
    def create(self,request):
        is_new='0'
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            ttp=profile.get("id",0)
            pzq=profile.get("email",0)
            if ttp==0 or pzq==0:
                logging.debug('MAIL o ID')
                return Response(status=status.HTTP_204_NO_CONTENT)
            try:
                u=Users.objects.get(users_email=profile["email"])
                u.users_fb_id=profile["id"]
                u.users_time_zone=profile.get('timezone',None)
                u.users_locale=profile.get('locale',None)
                u.users_middle_name=profile.get('middle_name',None)
                u.users_name_id=profile.get("username",profile["id"])
                u.users_birthday=profile.get('birthday',None)
                #u.users_device=self.request.user_agent.os.family
                if u.users_birthday is not None:
                    u.users_birthday=datetime.strptime(u.users_birthday,'%m/%d/%Y').date()
                #u.users_age_range=profile.get("age_range",'')
                u.save()
                sn=SocialNetworks.objects.get(fk_users=u)
                sn.social_networks_enable=1
                sn.save()
            except Users.DoesNotExist:
                u_birthday=profile.get('birthday',None)
                if u_birthday is not None:
                    u_birthday=datetime.strptime(u_birthday,'%m/%d/%Y').date()
                pass_hash=hashlib.sha1(str(random.uniform(1, 999999))+str(time.time())).hexdigest()
                Users(users_firstname=profile.get("first_name",None),users_lastname=profile.get("last_name",None),users_name=profile.get("name",None),users_name_id=profile.get("username",profile["id"]),users_email=profile["email"],users_password=pass_hash,fk_users_type=UsersType.objects.get(users_type_id=1),users_delete=0,users_sex=profile.get('gender',None),users_fb_id=profile["id"],users_path_web_avatar="https://lh5.ggpht.com/Q4xVViXWwTbXXq2KTNunRhcUSg9BLN4hILmMRs7XMiGM_2iv_5BQyB2JtUOUVRdT4ymZNzftQpeM4tM1LnxwUcjklVwomg=s500",users_date_joined=time.strftime('%Y-%m-%d %H:%M:%S'),users_time_zone=profile.get('timezone',None),users_locale=profile.get('locale',None),users_birthday=u_birthday,users_middle_name=profile.get('middle_name',None)).save()
                u=Users.objects.get(users_email=profile["email"])
                Client(user_id=u.users_id,name=u.users_email,url='',redirect_uri='',client_id='02770b9b0452d7e56a1d',client_secret='0b671033626580921b56593440c3e387d0cb5ec6',client_type=1).save()
                #mixpanel=Mixpanel("87c672a0b3c66ee03ac32ddf4cc0b20b")
                #mixpanel.alias(profile["email"],None)
                #mixpanel.people_set(profile["email"],{'first_name':profile.get("name",""),'last_name':profile.get("last_name",""),'email':profile["email"],'created':time.strftime('%Y-%m-%dT%H:%M:%S')})
                
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                cursor_in=conn.cursor()
                try:
                    img=urllib2.urlopen(urllib2.Request('https://graph.facebook.com/'+profile["id"]+'/picture?type=small'),timeout=120)
                    
                    cursor_in.execute('SELECT users_path_local_avatar from users where users_path_local_avatar=%s and users_id=%s',(img.geturl(),u.users_id))
                    upla=cursor_in.fetchone()
                    if upla==None:
                        file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
                        file_name=files.blobstore.create(mime_type='application/octet-stream',_blobinfo_uploaded_filename=file_name_hash)
                        with files.open(file_name,'ab') as f:
                            while True:
                                chunk=img.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        files.finalize(file_name)
                        blob_key=files.blobstore.get_blob_key(file_name)
                        #blob_info=BlobInfo.get(blob_key)
                        file_name_hash=images.get_serving_url(blob_key,size=500)                    
                        cursor_in.execute('UPDATE users SET users_path_web_avatar=%s,users_path_local_avatar=%s WHERE users_id=%s',('https://'+file_name_hash[7:],img.geturl(),u.users_id))
                        conn.commit()
                    cursor_in.close()
                    conn.close()
                except:
                    cursor_in.close()
                    conn.close()
                is_new='1'
            else:
                u=Users.objects.get(users_email=profile["email"])
                pass_hash=u.users_password
            serializer.object.fk_users=u
            serializer.object.users_network_id=profile["id"]
            serializer.object.social_networks_enable=1
            serializer.object.social_networks_expires_in=0
            headers = self.get_success_headers(serializer.data)
            try:
                x=SocialNetworks.objects.get(fk_networks_type=serializer.object.fk_networks_type,fk_users=u)
                x.social_networks_token=serializer.object.social_networks_token
                x.save()
            except SocialNetworks.DoesNotExist:
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
            opener = urllib2.build_opener()
            opener.addheaders = [('', '')]
            try:
                data=urllib.urlencode({'client_id':'02770b9b0452d7e56a1d','client_secret':'0b671033626580921b56593440c3e387d0cb5ec6','grant_type':'password','users_email':str(profile["email"]),'password':str(pass_hash)})
                res=opener.open('https://festive-ally-585.appspot.com/oauth2/access_token/',data,60)
                j = res.read()
                j_obj=json.loads(j)
                j_obj['is_new']=is_new
                return Response(j_obj,status=status.HTTP_201_CREATED,headers=headers)
            except urllib2.HTTPError, err:
                if err.code == 404:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class UsersFollowsEventsViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class=UserFollowEventSerializer
    queryset=UsersFollowsEvents.objects.order_by('users_follows_events_id')
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        key=self.request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist,e:
                return Response({'Error':'Token does not exist.'})
        request.DATA['fk_users']=token_user
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            try:
                ufe=UsersFollowsEvents.objects.get(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events)
            except UsersFollowsEvents.DoesNotExist:
                serializer.object.users_follows_events_subscription_date=datetime.now()
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                #Activities(user_id=serializer.object.fk_events.fk_user_creator.users_id,user_action_id=serializer.object.fk_users.users_id,action=2,object=serializer.object.fk_events.events_id,activities_date=datetime.now()).save(force_insert=True)
                notifAll(serializer.object.fk_events.events_id,serializer.object.fk_users.users_id,2)
                return Response({"status":"follow"},status=status.HTTP_201_CREATED)
            except UsersFollowsEvents.MultipleObjectsReturned:
                UsersFollowsEvents.objects.filter(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events).delete()
                UsersUnfollowsEvents.objects.filter(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events).delete()
                UsersUnfollowsEvents(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events,users_follows_events_unsubscribe_date=datetime.now()).save()
                return Response({"status":"not_follow"},status=status.HTTP_201_CREATED)
            else:
                UsersUnfollowsEvents.objects.filter(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events).delete()
                UsersUnfollowsEvents(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events,users_follows_events_unsubscribe_date=datetime.now()).save()
                ufe.delete()
                return Response({"status":"not_follow"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
from django.utils import simplejson
class UsersWritesCommentsViewSet(viewsets.ModelViewSet):
    authentication_classes=(OAuth2Authentication,)
    permission_classes=(IsAuthenticated,)
    serializer_class=UserWriteCommentSerializer
    queryset=UsersWritesComments.objects.all()
    def list(self,request):
        events_id=self.request.QUERY_PARAMS.get('fk_events','')
        queryset=UsersWritesComments.objects.all()
        if events_id!='':
            queryset=UsersWritesComments.objects.filter(fk_events=str(events_id)).order_by('-users_writes_comments_id')
            paginator=Paginator(queryset,100)
            page=request.QUERY_PARAMS.get('page')
            try:
                comments=paginator.page(page)
            except PageNotAnInteger:
                comments=paginator.page(1)
            except EmptyPage:
                comments=paginator.page(paginator.num_pages)
            serializer_context={'request':request}
            serializer=PaginatedUserWriteCommentSerializer(comments,context=serializer_context)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        token_user=getUserIdByToken(self.request.META.get('HTTP_AUTHORIZATION'))
        request.DATA['fk_users']=token_user
        serializer=self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            c=Comments(comments_value=serializer.object.users_writes_comments_content)
            c.save()
            serializer.object.fk_comments=c
            serializer.object.users_writes_comments_delete=0
            self.pre_save(serializer.object)
            self.object=serializer.save(force_insert=True)
            self.post_save(self.object,created=True)
            pubnub=notifsocket()
            pubnub.publish({
                'channel':'comm_'+str(serializer.object.fk_events.events_id),
                'message':{
                    'comment_id':str(c.comments_id),
                    'u_name_id':serializer.object.fk_users.users_name_id,
                    'u_id':serializer.object.fk_users.users_id,
                    'u_name':serializer.object.fk_users.users_name,
                    'u_photo':serializer.object.fk_users.users_path_web_avatar,
                    'msg':serializer.object.users_writes_comments_content,
                    'secs':str(serializer.data['comments_seconds'])
                }
            })
            #ufe=UsersFollowsEvents.objects.filter(fk_events=serializer.object.fk_events.events_id)
            #for uuu in ufe:
            #    Activities(user_id=uuu.fk_users.users_id,user_action_id=serializer.object.fk_users.users_id,action=3,object=serializer.object.fk_events.events_id,activities_date=datetime.now()).save(force_insert=True)
            #Activities(user_id=serializer.object.fk_events.fk_user_creator.users_id,user_action_id=serializer.object.fk_users.users_id,action=3,object=serializer.object.fk_events.events_id,activities_date=datetime.now()).save(force_insert=True)
            notifAll(serializer.object.fk_events.events_id,serializer.object.fk_users.users_id,4)
            
            return Response({
                    'comment_id':str(c.comments_id),
                    'u_name_id':serializer.object.fk_users.users_name_id,
                    'u_id':serializer.object.fk_users.users_id,
                    'u_name':serializer.object.fk_users.users_name,
                    'u_photo':serializer.object.fk_users.users_path_web_avatar,
                    'msg':serializer.object.users_writes_comments_content,
                    'secs':str(serializer.data['comments_seconds'])
                },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self,request,pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request,pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self,request,pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self,request,pk=None):
        token_user=getUserIdByToken(self.request.META.get('HTTP_AUTHORIZATION'))
        queryset=Comments.objects.all()
        comment=get_object_or_404(queryset,pk=pk)
        try:
            userwritecomment=UsersWritesComments.objects.get(fk_comments=comment.comments_id)
            if userwritecomment.fk_users.users_id==token_user:
                userwritecomment.users_writes_comments_delete=1
                userwritecomment.save()
                return Response({'comments_id':comment.comments_id},status=status.HTTP_200_OK)
            else:
                return Response({},status=status.HTTP_401_UNAUTHORIZED)
            return Response('',status=status.HTTP_401_UNAUTHORIZED)
        except UsersWritesComments.DoesNotExist:
            return Response('',status=status.HTTP_401_UNAUTHORIZED)
class SharedEventsViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class=SharedEventSerializer
    queryset=SharedEvents.objects.all()
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        key=self.request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist, e:
                return Response({'Error': 'Token does not exist.'})
        request.DATA['fk_users']=token_user
        serializer=self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object=serializer.save(force_insert=True)
            self.post_save(self.object,created=True)
            headers=self.get_success_headers(serializer.data)
            return Response({'status':'shared'},status=status.HTTP_201_CREATED,headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class UsersHideEventsViewSet(viewsets.ModelViewSet):
    authentication_classes=(OAuth2Authentication,)
    permission_classes=(IsAuthenticated,)
    serializer_class=UserHideEventSerializer
    queryset=UsersHideEvents.objects.all()
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self, request):
        key=self.request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token = AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires < datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist, e:
                return Response({'Error': 'Token does not exist.'})
        request.DATA['fk_users']=token_user
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            try:
                uhe=UsersHideEvents.objects.get(fk_users=serializer.object.fk_users,fk_events=serializer.object.fk_events)
                return Response({'status':'hidden'}, status=status.HTTP_202_ACCEPTED)
            except UsersHideEvents.DoesNotExist:
                ehh=EventsHasHashtags.objects.filter(fk_events=serializer.object.fk_events)
                for evhh in ehh:
                    uhh=UsersHasHashtags.objects.get(fk_hashtags=evhh.fk_hashtags)
                    uhh.users_has_hashtags_weight=uhh.users_has_hashtags_weight-0.1
                    uhh.save()
                self.pre_save(serializer.object)
                self.object=serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                return Response({'status':'hidden'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class InvitationsViewSet(viewsets.ModelViewSet):
    authentication_classes=(OAuth2Authentication,)
    permission_classes=(IsAuthenticated,)
    serializer_class=InvitationSerializer
    queryset=Invitations.objects.all()
    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self,request,*args,**kwargs):
        key=self.request.META.get('HTTP_AUTHORIZATION')
        if not key:
            return Response({'Error':'No token provided.'})
        else:
            try:
                token=AccessToken.objects.get(token=key.replace("Bearer","").strip())
                if not token:
                    return Response({'Error':'Access denied.'})
                if token.expires<datetime.now():
                    return Response({'Error':'Token has expired.'})
                else:
                    token_user=token.user_id
            except AccessToken.DoesNotExist, e:
                return Response({'Error': 'Token does not exist.'})
        request.DATA['request']=token_user
        serializer=self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            hash=hashlib.sha1(str(random.uniform(1, 999999))+str(time.time())).hexdigest()
            serializer.object.hash=hash
            self.pre_save(serializer.object)
            self.object=serializer.save(force_insert=True)
            self.post_save(self.object,created=True)
            #enviar mail
            ms=Mandrill_Services()
            template_values={'hash':hash}
            t=loader.get_template('oclock/mail/invitation_friend.html')
            c=RequestContext(request,template_values)
            html=t.render(c)
            if ms.send_mail(serializer.object.email,'Invitation',html)>0:
                return Response({'status':'SENT'},status=status.HTTP_201_CREATED)
            else:
                return Response({'status':'ERROR'},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
class EventSpecialViewSet(viewsets.ModelViewSet):
    authentication_classes=(OAuth2Authentication,)
    permission_classes=(IsAuthenticated,)
    serializer_class=EventSpecialSerializer
    parser_classes=(FileUploadParser,)
    queryset=Events.objects.all()
    def list(self,request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def create(self,request):
        token_user=getUserIdByToken(self.request.META.get('HTTP_AUTHORIZATION'))
        request.DATA['fk_user_creator']='/api/users/%s/'%str(token_user)
        serializer=self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            country=getCountryByIP(request.META.get('REMOTE_ADDR'),serializer.object.events_ip)
            utz=Users.objects.get(users_id=token_user)
            u_zone=0
            n_min=0
            try:
                fb_ids=json.loads(serializer.object.events_fb_ids)
            except:
                return Response({"status":"error in fb_ids"},status=status.HTTP_400_BAD_REQUEST)
            if utz.users_time_zone is not None:
                u_zone=int(utz.users_time_zone)
            if serializer.object.events_type.strip()!='1' and serializer.object.events_type.strip()!='2':
                return Response({"status":"error in events_type"}, status=status.HTTP_400_BAD_REQUEST)
            elif serializer.object.events_type.strip()=='1' and serializer.object.events_start is not None:
                serializer.object.events_finish=None
                if u_zone>0: 
                    serializer.object.events_start-=timedelta(hours=u_zone)
                else:
                    serializer.object.events_start+=timedelta(hours=u_zone*(-1))
            elif serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                serializer.object.events_start=None
                if u_zone>0:
                    serializer.object.events_finish-=timedelta(hours=u_zone)
                else:
                    serializer.object.events_finish+=timedelta(hours=u_zone*(-1))
            if serializer.object.events_type.strip()=='1' and (serializer.object.events_start is None or serializer.object.events_start=='' or serializer.object.events_start>datetime.now()):
                return Response({"status":"error in events_start"},status=status.HTTP_400_BAD_REQUEST)
            if serializer.object.events_type.strip()=='2' and (serializer.object.events_finish is None or serializer.object.events_finish=='' or serializer.object.events_finish<=datetime.now()):
                return Response({"status":"error in events_finish"},status=status.HTTP_400_BAD_REQUEST)
            file_name_hash=None
            try:
                imm=request.FILES['events_image']
                file_name_hashs=init_image(imm,1)
                file_name_hash=file_name_hashs[0]
                if type(file_name_hashs) is int:
                    return Response({"image":["error %s."%(str(file_name_hash))]},status=status.HTTP_400_BAD_REQUEST)
                if serializer.object.events_ip is None or serializer.object.events_ip.strip()=='':
                    serializer.object.events_ip=request.META.get('REMOTE_ADDR')
                serializer.object.events_velocity=1000
                serializer.object.events_level=1
                serializer.object.events_delete=0
                serializer.object.events_enable=1
                serializer.object.events_cc=country
                serializer.object.events_sort=0
                serializer.object.events_type_special='love'
                serializer.object.events_image_stamp=file_name_hashs[1]
                if serializer.object.events_skins==None or serializer.object.events_skins=="":
                    serializer.object.events_skins="skin1"
                serializer.object.events_image=file_name_hash
                e_title=serializer.object.events_title.replace('-', ' ').strip()
                e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                e_title=slugify(e_title)
                if len(e_title.strip())==0:
                    e_title='oclock'; 
                #verificar si existe
                n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                if n_title > 0: 
                    serializer.object.events_title_id=e_title+'-'+str(n_title)
                else:
                    serializer.object.events_title_id=e_title
                #serializer.save()
                self.pre_save(serializer.object)
                self.object=serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                
                serializer.object.hashtags='ValentinesClock,'
                
                if serializer.object.hashtags.strip()=="" or serializer.object.hashtags is None:
                    hashs=serializer.object.events_title.split(' ')
                    for hash in hashs:
                        try:
                            e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                            hashtag=Hashtags.objects.get(hashtags_value=slugify(hash.replace('?', ' ').strip()))
                            try:
                                uhhashtag=EventsHasHashtags.objects.get(fk_events=e,fk_hashtags=hashtag)
                            except EventsHasHashtags.DoesNotExist:
                                uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            pass
                hashs=serializer.object.hashtags.split(',')
                for hash in hashs:
                    if hash.strip()!="" and len(hash)<=15:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                        hash_str=hash.strip()
                        hash=slugify(hash.replace('?', ' ').strip())
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            hashtag=Hashtags(hashtags_value=hash,hashtags_value_str=hash).save()
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                headers=self.get_success_headers(serializer.data)
                if serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                    pass
                
                UsersFollowsEvents(fk_users=utz,fk_events=Events.objects.get(events_id=serializer.data['events_id'])).save(force_insert=True)
                EventsAfter(events_after_content=serializer.object.events_msg,events_after_type='message',fk_events=serializer.data['events_id']).save()
                #u_fb_idq=serializer.object.events_fb_ids[1:-1]
                #u_fb_idq_arr=u_fb_idq.split(',')[:-1]
                try:
                    if len(fb_ids['data'])>0:
                        for idgo in fb_ids['data']:
                            EventsInvitations(fk_users_from=token_user,fk_users_to=idgo,fk_events=serializer.data['events_id'],events_invitations_date=datetime.now()).save()
                    else:
                        return Response({"status":"error in fb_ids"},status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"status":"error in fb_ids"},status=status.HTTP_400_BAD_REQUEST)
                
                return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except MultiValueDictKeyError:
                if serializer.object.events_ip is None or serializer.object.events_ip.strip()=='':
                    serializer.object.events_ip=request.META.get('REMOTE_ADDR')
                serializer.object.events_velocity=1000
                serializer.object.events_level=1
                serializer.object.events_delete=0
                serializer.object.events_enable=1
                serializer.object.events_cc=country
                serializer.object.events_sort=0
                serializer.object.events_image=serializer.object.events_img_str
                serializer.object.events_type_special='love'
                serializer.object.events_image_stamp='https://storage.googleapis.com/oclock-images/default.jpg'
                if serializer.object.events_skins==None or serializer.object.events_skins=="":
                    serializer.object.events_skins="skin1"
                #serializer.object.events_image=file_name_hash
                e_title=serializer.object.events_title.replace('-', ' ').strip()
                e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                e_title=slugify(e_title)
                if len(e_title.strip())==0:
                    e_title='oclock'; 
                n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                if n_title>0: 
                    serializer.object.events_title_id=e_title+'-'+str(n_title)
                else:
                    serializer.object.events_title_id=e_title
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object,created=True)
                if serializer.object.hashtags.strip()=="" or serializer.object.hashtags is None:
                    hashs=serializer.object.events_title.split(' ')
                    for hash in hashs:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                        hash=slugify(hash.replace('?', ' ').strip())
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            #if hashtag is None:
                            #hashtag=Hashtags(hashtags_value=hash).save()
                            #hashtag=Hashtags.objects.get(hashtags_value=hash)
                            pass
                hashs=serializer.object.hashtags.split(',')
                for hash in hashs:
                    if hash.strip()!="" and len(hash)<=15:
                        e=Events.objects.get(events_title_id=serializer.object.events_title_id)
                        hash_str=hash.strip()
                        hash=slugify(hash.replace('?', ' ').strip())
                        try:
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                        except Hashtags.DoesNotExist:
                            hashtag=Hashtags(hashtags_value=hash,hashtags_value_str=hash).save()
                            hashtag=Hashtags.objects.get(hashtags_value=hash)
                            uhhashtag=EventsHasHashtags(fk_events=e,fk_hashtags=hashtag).save()
                headers = self.get_success_headers(serializer.data)
                if serializer.object.events_type.strip()=='2' and serializer.object.events_finish is not None:
                    pass
                
                UsersFollowsEvents(fk_users=utz,fk_events=Events.objects.get(events_id=serializer.data['events_id'])).save(force_insert=True)
                EventsAfter(events_after_content=serializer.object.events_msg,events_after_type='message',fk_events=serializer.data['events_id']).save()
                #u_fb_idq=serializer.object.events_fb_ids[1:-1]
                #u_fb_idq_arr=u_fb_idq.split(',')[:-1]
                try:
                    if len(fb_ids['data'])>0:
                        for idgo in fb_ids['data']:
                            EventsInvitations(fk_users_from=token_user,fk_users_to=idgo,fk_events=serializer.data['events_id'],events_invitations_date=datetime.now()).save()
                    else:
                        return Response({"status":"error in fb_ids"},status=status.HTTP_400_BAD_REQUEST)
                except Exception, e:
                    return Response({"status":"error in fb_ids"},status=status.HTTP_400_BAD_REQUEST)
                
                return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)