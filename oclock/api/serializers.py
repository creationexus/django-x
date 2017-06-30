'''
Created on 23-06-2014
@author: carriagadad
'''
from oclock.apps.db.models import Users,UsersType,Events,UsersRequestEmail,SharedEvents,UsersHideEvents,Comments,Invitations,EventsSpecial
from oclock.apps.db.models import Hashtags,UsersHasHashtags,NetworksType,SocialNetworks,UsersFollowsEvents,UsersWritesComments
from rest_framework import serializers,pagination 
from oclock.api.ExampleAuthentication import ExampleAuthentication
from django.utils.timezone import now
from django.db import models
class UserSerializer(serializers.HyperlinkedModelSerializer):
    hashtags=serializers.RelatedField(many=True)
    events=serializers.RelatedField(many=True)
    users_password=serializers.CharField(required=True,write_only=True)
    users_email=serializers.CharField(required=True, write_only=True)
    users_name_id=serializers.CharField(max_length=255,required=True)
    users_path_web_avatar=serializers.SerializerMethodField('image')
    def image(self,obj):
        if obj.users_path_web_avatar==None:
            return 'https://festive-ally-585.appspot.com/static/images/default.jpg'
        return obj.users_path_web_avatar
    class Meta:
        model = Users
        fields = ('users_id','users_name','users_name_id','users_firstname','users_lastname','users_email','users_password','users_path_local_avatar','users_path_web_avatar','users_time_zone','fk_users_type','users_delete','users_birthday','users_sex','hashtags','events','users_hashtags','users_is_location_enable')
        read_only_fields=('users_id','users_delete','fk_users_type')
        #authentication = Authentication()
        #authorization = Authorization()
        #include_resource_uri = False
        #excludes = ['fk_users_type','users_delete']
        #authentication = ExampleAuthentication()
        #allowed_methods = ['get','post']
        #depth = 1
        #write_only_fields = ('users_password','users_delete')  # Note: Password field is write-only
        #required_fields = ('users_password')
        #write_only_fields=('users_password',)
class PaginatedUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        object_serializer_class = UserSerializer
class UserTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UsersType
        fields = ('users_type_id','users_type_name')
        read_only_fields = ('users_type_id',)
class EventSerializer(serializers.HyperlinkedModelSerializer):
    events_seconds=serializers.SerializerMethodField('seconds')
    events_title_id=serializers.SerializerMethodField('str_id')
    events_image=serializers.SerializerMethodField('image')
    events_follows=serializers.RelatedField(many=True)
    events_comments=serializers.RelatedField(many=True)
    shared_events_e=serializers.RelatedField(many=True)
    fk_users=UserSerializer(source='fk_user_creator',required=False)
    events_start=serializers.DateTimeField(required=False)
    events_title=serializers.CharField(required=True,max_length=200,min_length=1)
    events_finish=serializers.DateTimeField(required=False)
    events_hashtags=serializers.RelatedField(many=True)
    def seconds(self,obj):
        if obj.events_type == 'timer':
            if obj.events_start is None:
                return 0
            else:
                return long((now()-obj.events_start).total_seconds())
        else:
            if obj.events_finish is None:
                return 0
            else:
                return long((obj.events_finish-now()).total_seconds())
    def str_id(self,obj):
        return str(obj.events_title_id)
    def image(self,obj):
        if obj.events_image==None:
            return 'https://festive-ally-585.appspot.com/static/images/default.jpg'
        return obj.events_image
    class Meta:
        model = Events
        fields=('events_id','events_title','events_title_id','events_description','events_latitude','events_longitude','events_start','events_finish','events_type','fk_user_creator','events_language','events_country','events_velocity','events_image','events_seconds','events_level','events_skins','events_follows','events_comments','events_hashtags','hashtags','fk_users','shared_events_e','events_ip','events_img_str','events_image_stamp','events_tz')
        write_only_fields=('hashtags','fk_user_creator','events_cc','events_ip','events_img_str','events_image_stamp','events_tz')
        read_only_fields=('events_id',)
class PaginatedEventSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class=EventSerializer
class ResetPasswordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        allowed_methods = ['post']
        list_allowed_methods = ['post']
        #detail_allowed_methods = ['get', 'post', 'put', 'delete']
        detail_allowed_methods = ['get']
        model = Users
        fields = ('users_id','users_email',)
        read_only_fields = ('users_id',)
class UserRequestEmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UsersRequestEmail
        fields = ('fk_users_id','users_request_email_hash',)
        read_only_fields = ('fk_users_id','users_request_email_hash')
class UserHasHashtagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=UsersHasHashtags
        fields=('users_has_hashtags_id','fk_users','fk_hashtags',)
        read_only_fields = ('users_has_hashtags_id',)
class HashtagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Hashtags
        fields=('hashtags_id','hashtags_value',)
        read_only_fields = ('hashtags_id',)
class SocialNetworkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=SocialNetworks
        fields=('social_networks_id','users_network_id','fk_users','fk_networks_type','social_networks_token','social_networks_enable')
        read_only_fields = ('social_networks_id','fk_users')
class NetworkTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=NetworksType
        fields=('networks_type_id','networks_type_name')
        read_only_fields = ('networks_type_id',)
class UserFollowEventSerializer(serializers.HyperlinkedModelSerializer):
    users_follows_events_unsubscribe_date=serializers.DateTimeField(required=False,write_only=True)
    fk_users=serializers.PrimaryKeyRelatedField(many=False)
    fk_events=serializers.PrimaryKeyRelatedField(many=False)
    class Meta:
        model=UsersFollowsEvents
        fields=('users_follows_events_id','users_follows_events_subscription_date','users_follows_events_unsubscribe_date','fk_users','fk_events')
        read_only_fields = ('users_follows_events_id',)
class CommentSerializer(serializers.HyperlinkedModelSerializer):
    comments_seconds=serializers.SerializerMethodField('seconds')
    def seconds(self,obj):
        if obj.comments_date is None:
            return 0
        else:
            return long((now()-obj.comments_date).total_seconds())
    class Meta:
        model=Comments
        fields=('comments_id','comments_value','comments_date','comments_seconds')
        read_only_fields = ('comments_id',)
class PaginatedCommentSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class=CommentSerializer
class UserWriteCommentSerializer(serializers.HyperlinkedModelSerializer):
    fk_comments=serializers.CharField(required=False)
    users_writes_comments_content=serializers.CharField(max_length=300,min_length=1,required=True)
    fk_users=serializers.PrimaryKeyRelatedField(many=False)
    fk_events=serializers.PrimaryKeyRelatedField(many=False)
    users_name_id=serializers.Field(source='fk_users.users_name_id')
    comments_value=serializers.Field(source='fk_comments.comments_value')
    comments_date=serializers.Field(source='fk_comments.comments_date')
    comments_seconds=serializers.SerializerMethodField('seconds')
    def seconds(self,obj):
        if obj.fk_comments.comments_date is None:
            return 0
        else:
            return long((now()-obj.fk_comments.comments_date).total_seconds())
    class Meta:
        model=UsersWritesComments
        fields=('fk_comments','users_writes_comments_content','fk_users','fk_events','users_writes_comments_delete','fk_comments','users_name_id','comments_value','comments_date','comments_seconds')
        #read_only_fields=('users_writes_comments_id',)
        write_only_fields=('users_writes_comments_delete',)
class PaginatedUserWriteCommentSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class=UserWriteCommentSerializer
class SharedEventSerializer(serializers.HyperlinkedModelSerializer):
    fk_events=serializers.PrimaryKeyRelatedField(many=False)
    fk_users=serializers.PrimaryKeyRelatedField(many=False)
    class Meta:
        model=SharedEvents
        fields=('fk_events','fk_users')
class UserHideEventSerializer(serializers.HyperlinkedModelSerializer):
    fk_events=serializers.PrimaryKeyRelatedField(many=False)
    fk_users=serializers.PrimaryKeyRelatedField(many=False)
    class Meta:
        model=UsersHideEvents
        fields=('fk_users','fk_events')
class InvitationSerializer(serializers.HyperlinkedModelSerializer):
    request=serializers.PrimaryKeyRelatedField(many=False)
    email=serializers.CharField(max_length=255,min_length=1,required=True)
    hash=serializers.CharField(max_length=300,min_length=1,required=False)
    invitation_dt=serializers.DateTimeField(required=False,write_only=True)
    class Meta:
        model=Invitations
        fields=('request','email','hash')
class EventSpecialSerializer(serializers.HyperlinkedModelSerializer):
    events_seconds=serializers.SerializerMethodField('seconds')
    events_title_id=serializers.SerializerMethodField('str_id')
    events_image=serializers.SerializerMethodField('image')
    events_follows=serializers.RelatedField(many=True)
    events_comments=serializers.RelatedField(many=True)
    shared_events_e=serializers.RelatedField(many=True)
    fk_users=UserSerializer(source='fk_user_creator',required=False)
    events_start=serializers.DateTimeField(required=False)
    events_title=serializers.CharField(required=True,max_length=200,min_length=1)
    events_finish=serializers.DateTimeField(required=False)
    events_hashtags=serializers.RelatedField(many=True)
    def seconds(self,obj):
        if obj.events_type == 'timer':
            if obj.events_start is None:
                return 0
            else:
                return long((now()-obj.events_start).total_seconds())
        else:
            if obj.events_finish is None:
                return 0
            else:
                return long((obj.events_finish-now()).total_seconds())
    def str_id(self,obj):
        return str(obj.events_title_id)
    def image(self,obj):
        if obj.events_image==None:
            return 'https://festive-ally-585.appspot.com/static/images/default.jpg'
        return obj.events_image
    class Meta:
        model=Events
        fields=('events_id','events_title','events_title_id','events_description','events_latitude','events_longitude','events_start','events_finish','events_type','fk_user_creator','events_language','events_country','events_velocity','events_image','events_seconds','events_level','events_skins','events_follows','events_comments','events_hashtags','hashtags','fk_users','shared_events_e','events_ip','events_fb_ids','events_msg','events_img_str','events_type_special')
        write_only_fields=('hashtags','fk_user_creator','events_cc','events_ip','events_fb_ids','events_msg','events_img_str','events_type_special')
        read_only_fields=('events_id',)    