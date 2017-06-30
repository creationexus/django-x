'''
Created on 02-06-2014
@author: carriagadad
'''
from django.db import models
class UsersType(models.Model):
    users_type_id=models.BigIntegerField(primary_key=True)
    users_type_name=models.CharField(max_length=300,blank=True)
    class Meta:
        db_table=u'users_type'
class Users(models.Model):
    users_id=models.BigIntegerField(primary_key=True)
    users_name=models.CharField(max_length=500,blank=False)
    users_name_id=models.CharField(max_length=255,blank=False,unique=True)
    users_lastname=models.CharField(max_length=300,blank=True)
    users_firstname=models.CharField(max_length=300,blank=True)
    users_email=models.CharField(max_length=255,blank=True,unique=True)
    users_password=models.CharField(max_length=300,blank=True)
    users_fb_id=models.CharField(max_length=100,blank=True)
    users_path_local_avatar=models.CharField(max_length=500,blank=True)
    users_path_web_avatar=models.CharField(max_length=500,blank=True)
    users_time_zone=models.CharField(max_length=45,blank=True)
    fk_users_type=models.ForeignKey(UsersType,db_column=u'fk_users_type')
    users_delete=models.IntegerField(null=True, blank=True)
    users_birthday=models.DateTimeField(null=True, blank=True)
    users_sex=models.CharField(max_length=6,blank=True)
    #users_hashtags=models.ManyToManyField('Hashtags',through='UsersHasHashtags')
    users_hashtags=models.CharField(max_length=300,blank=True)
    users_date_joined=models.DateTimeField(blank=True)
    users_locale=models.CharField(max_length=5,blank=True)
    users_middle_name=models.CharField(max_length=300,blank=True)
    users_is_location_enable=models.BooleanField(db_column=u'users_is_location_enable')
    users_is_nearby_enable=models.BooleanField(db_column=u'users_is_nearby_enable')
    users_device=models.CharField(max_length=50,blank=True)
    users_channel=models.CharField(max_length=50,blank=True)
    class Meta:
        db_table=u'users'
    def __unicode__(self):
        return '%d: %s'%(self.users_id,self.users_name)
    def is_authenticated(self):
        return True
class UsersRequestEmail(models.Model):
    users_request_email_id=models.BigIntegerField(primary_key=True)
    fk_users=models.ForeignKey(Users,db_column=u'fk_users')
    users_request_email_hash=models.CharField(max_length=100,blank=False)
    users_request_email_enable=models.BooleanField(blank=False)
    class Meta:
        db_table=u'users_request_email'
class Events(models.Model):
    #events_id=models.BigIntegerField(primary_key=True,db_column=u'events_id')
    events_id=models.AutoField(primary_key=True,db_column=u'events_id')
    events_title=models.CharField(max_length=200,blank=True)
    events_description=models.CharField(max_length=500,blank=True)
    events_latitude=models.CharField(max_length=45,blank=True)
    events_longitude=models.CharField(max_length=45,blank=True)
    events_start=models.DateTimeField(null=True,blank=True)
    events_finish=models.DateTimeField(null=True,blank=True)
    events_type=models.CharField(max_length=10,blank=True)
    fk_user_creator=models.ForeignKey(Users,db_column=u'fk_user_creator',related_name='events')
    events_enable=models.IntegerField(null=True,blank=True)
    events_delete=models.IntegerField(null=True,blank=True)
    events_language=models.CharField(max_length=5,blank=True)
    events_country=models.CharField(max_length=45,blank=True)
    events_velocity=models.IntegerField(null=True,blank=True)
    events_image=models.CharField(max_length=250,blank=True)
    events_level=models.CharField(max_length=10,blank=True)
    events_title_id=models.CharField(max_length=200,blank=True)
    events_skins=models.CharField(max_length=5,blank=True)
    events_fb_event_id=models.CharField(max_length=300,blank=True)
    events_date_creation=models.DateTimeField(blank=True)
    hashtags=models.CharField(max_length=300,blank=True)
    events_cc=models.CharField(max_length=2,blank=True)
    events_ip=models.CharField(max_length=15,blank=True)
    events_fb_ids=models.TextField(null=True,blank=True)
    events_msg=models.CharField(max_length=500,blank=True)
    events_img_str=models.CharField(max_length=300,blank=True)
    events_sort=models.BigIntegerField()
    events_type_special=models.CharField(max_length=100,blank=True)
    events_image_stamp=models.CharField(max_length=250,blank=True)
    events_tz=models.CharField(max_length=11,blank=True,null=True)
    class Meta:
        db_table=u'events'
    def __unicode__(self):
        return '%d: %s'%(self.events_id,self.events_title)
class EventsSpecial(models.Model):
    #events_id=models.BigIntegerField(primary_key=True,db_column=u'events_id')
    events_id=models.AutoField(primary_key=True,db_column=u'events_id')
    events_title=models.CharField(max_length=200,blank=True)
    events_description=models.CharField(max_length=500,blank=True)
    events_latitude=models.CharField(max_length=45,blank=True)
    events_longitude=models.CharField(max_length=45,blank=True)
    events_start=models.DateTimeField(null=True,blank=True)
    events_finish=models.DateTimeField(null=True,blank=True)
    events_type=models.CharField(max_length=10,blank=True)
    fk_user_creator=models.ForeignKey(Users,db_column=u'fk_user_creator',related_name='events')
    events_enable=models.IntegerField(null=True,blank=True)
    events_delete=models.IntegerField(null=True,blank=True)
    events_language=models.CharField(max_length=5,blank=True)
    events_country=models.CharField(max_length=45,blank=True)
    events_velocity=models.IntegerField(null=True,blank=True)
    events_image=models.CharField(max_length=250,blank=True)
    events_level=models.CharField(max_length=10,blank=True)
    events_title_id=models.CharField(max_length=200,blank=True)
    events_skins=models.CharField(max_length=5,blank=True)
    events_fb_event_id=models.CharField(max_length=300,blank=True)
    events_date_creation=models.DateTimeField(blank=True)
    hashtags=models.CharField(max_length=300,blank=True)
    events_cc=models.CharField(max_length=2,blank=True)
    events_ip=models.CharField(max_length=15,blank=True)
    events_fb_ids=models.TextField(null=False,blank=False)
    events_msg=models.CharField(max_length=500,blank=True)
    events_img_str=models.CharField(max_length=300,blank=True)
    events_sort=models.BigIntegerField()
    events_type_special=models.CharField(max_length=100,blank=True)
    class Meta:
        db_table=u'events'
    def __unicode__(self):
        return '%d: %s'%(self.events_id,self.events_title)
class EventsLow(models.Model):
    events_id=models.BigIntegerField(primary_key=True,db_column=u'events_id')
    #events_id=models.AutoField(primary_key=True,db_column=u'events_id')
    events_title=models.CharField(max_length=200,blank=True)
    events_description=models.CharField(max_length=500,blank=True)
    events_latitude=models.CharField(max_length=45,blank=True)
    events_longitude=models.CharField(max_length=45,blank=True)
    events_start=models.DateTimeField(null=True,blank=True)
    events_finish=models.DateTimeField(null=True,blank=True)
    events_type=models.CharField(max_length=10,blank=True)
    fk_user_creator=models.ForeignKey(Users,db_column=u'fk_user_creator')
    events_enable=models.IntegerField(null=True,blank=True)
    events_delete=models.IntegerField(null=True,blank=True)
    events_language=models.CharField(max_length=5,blank=True)
    events_country=models.CharField(max_length=45,blank=True)
    events_velocity=models.IntegerField(null=True,blank=True)
    events_image=models.CharField(max_length=250,blank=True)
    events_level=models.CharField(max_length=10,blank=True)
    events_title_id=models.CharField(max_length=200,blank=True)
    events_skins=models.CharField(max_length=5,blank=True)
    events_fb_event_id=models.CharField(max_length=300,blank=True)
    events_date_creation=models.DateTimeField(blank=True)
    hashtags=models.CharField(max_length=300,blank=True)
    class Meta:
        db_table=u'events_low'
class EventsMedium(models.Model):
    events_id=models.BigIntegerField(primary_key=True,db_column=u'events_id')
    #events_id=models.AutoField(primary_key=True,db_column=u'events_id')
    events_title=models.CharField(max_length=200,blank=True)
    events_description=models.CharField(max_length=500,blank=True)
    events_latitude=models.CharField(max_length=45,blank=True)
    events_longitude=models.CharField(max_length=45,blank=True)
    events_start=models.DateTimeField(null=True,blank=True)
    events_finish=models.DateTimeField(null=True,blank=True)
    events_type=models.CharField(max_length=10,blank=True)
    fk_user_creator=models.ForeignKey(Users,db_column=u'fk_user_creator')
    events_enable=models.IntegerField(null=True,blank=True)
    events_delete=models.IntegerField(null=True,blank=True)
    events_language=models.CharField(max_length=5,blank=True)
    events_country=models.CharField(max_length=45,blank=True)
    events_velocity=models.IntegerField(null=True,blank=True)
    events_image=models.CharField(max_length=250,blank=True)
    events_level=models.CharField(max_length=10,blank=True)
    events_title_id=models.CharField(max_length=200,blank=True)
    events_skins=models.CharField(max_length=5,blank=True)
    events_fb_event_id=models.CharField(max_length=300,blank=True)
    events_date_creation=models.DateTimeField(blank=True)
    hashtags=models.CharField(max_length=300,blank=True)
    class Meta:
        db_table=u'events_medium'
class EventsHigh(models.Model):
    events_id=models.BigIntegerField(primary_key=True,db_column=u'events_id')
    #events_id=models.AutoField(primary_key=True,db_column=u'events_id')
    events_title=models.CharField(max_length=200,blank=True)
    events_description=models.CharField(max_length=500,blank=True)
    events_latitude=models.CharField(max_length=45,blank=True)
    events_longitude=models.CharField(max_length=45,blank=True)
    events_start=models.DateTimeField(null=True,blank=True)
    events_finish=models.DateTimeField(null=True,blank=True)
    events_type=models.CharField(max_length=10,blank=True)
    fk_user_creator=models.ForeignKey(Users,db_column=u'fk_user_creator')
    events_enable=models.IntegerField(null=True,blank=True)
    events_delete=models.IntegerField(null=True,blank=True)
    events_language=models.CharField(max_length=5,blank=True)
    events_country=models.CharField(max_length=45,blank=True)
    events_velocity=models.IntegerField(null=True,blank=True)
    events_image=models.CharField(max_length=250,blank=True)
    events_level=models.CharField(max_length=10,blank=True)
    events_title_id=models.CharField(max_length=200,blank=True)
    events_skins=models.CharField(max_length=5,blank=True)
    events_fb_event_id=models.CharField(max_length=300,blank=True)
    events_date_creation=models.DateTimeField(blank=True)
    hashtags=models.CharField(max_length=300,blank=True)
    class Meta:
        db_table=u'events_high'
class Campaigns(models.Model):
    campaigns_id = models.BigIntegerField(primary_key=True)
    campaigns_nombre = models.CharField(blank=True)
    campaigns_saldo = models.FloatField(null=True,blank=True)
    campaigns_color = models.CharField(blank=True)
    campaigns_link = models.CharField(blank=True)
    campaigns_country = models.CharField(blank=True)
    fk_events = models.ForeignKey(Events,null=True,db_column=u'fk_events',blank=True)
    campaigns_active = models.IntegerField(null=True,blank=True)
    fk_users = models.ForeignKey(Users,db_column=u'fk_users')
    class Meta:
        db_table = u'campaigns'
class Country(models.Model):
    country_code=models.CharField(blank=True)
    country_name=models.CharField(blank=True)
    class Meta:
        db_table=u'country'
class Hashtags(models.Model):
    #hashtags_id=models.BigIntegerField(primary_key=True)
    hashtags_id=models.AutoField(primary_key=True,db_column=u'hashtags_id')
    hashtags_value=models.CharField(max_length=100,unique=True, blank=True)
    hashtags_value_str=models.CharField(max_length=100,unique=True,blank=True)
    class Meta:
        db_table=u'hashtags'
    def __unicode__(self):
        return '%d: %s'%(self.hashtags_id,self.hashtags_value)
class Invitations(models.Model):
    invitation_id=models.AutoField(primary_key=True,db_column=u'invitation_id')
    request=models.ForeignKey(Users,db_column=u'fk_users_from')
    email=models.CharField(null=False,blank=False,max_length=255,db_column=u'fk_users_email')
    hash=models.CharField(null=True,blank=True,max_length=300,db_column=u'invitation_hash')
    invitation_dt=models.DateTimeField()
    class Meta:
        db_table=u'invitations'
class EventsHasHashtags(models.Model):
    events_has_hashtags_id=models.BigIntegerField(primary_key=True)
    fk_events=models.ForeignKey(Events,db_column=u'fk_events',related_name='events_hashtags')
    fk_hashtags=models.ForeignKey(Hashtags,db_column=u'fk_hashtags')
    events_has_hashtags_date=models.DateTimeField()
    class Meta:
        db_table=u'events_has_hashtags'
    def __unicode__(self):
        return '%s'%(self.fk_hashtags)
class Multimedias(models.Model):
    multimedias_id = models.BigIntegerField(primary_key=True)
    multimedias_nombre = models.CharField(blank=True)
    multimedias_path_local = models.CharField(blank=True)
    multimedias_path_web = models.CharField(blank=True)
    multimedias_type = models.CharField(blank=True)
    fk_events = models.ForeignKey(Events, db_column=u'fk_events')
    class Meta:
        db_table=u'multimedias'
class NetworksType(models.Model):
    networks_type_id=models.IntegerField(primary_key=True)
    networks_type_name=models.CharField(max_length=45,blank=True)
    class Meta:
        db_table=u'networks_type'
class SharedEvents(models.Model):
    shared_eventos_id=models.BigIntegerField(primary_key=True,db_column=u'shared_eventos_id')
    fk_users=models.ForeignKey(Users,db_column=u'fk_users',related_name='shared_events_u')
    fk_events=models.ForeignKey(Events,db_column=u'fk_events',related_name='shared_events_e')
    class Meta:
        db_table=u'shared_events'
    def __unicode__(self):
        return '%s'%(self.fk_users)
class SocialNetworks(models.Model):
    social_networks_id=models.BigIntegerField(primary_key=True)
    users_network_id=models.CharField(max_length=100,blank=True)
    fk_users=models.ForeignKey(Users, db_column=u'fk_users')
    fk_networks_type=models.ForeignKey(NetworksType, db_column=u'fk_networks_type')
    social_networks_enable=models.IntegerField(null=True, blank=True)
    social_networks_token=models.CharField(max_length=500,blank=True)
    social_networks_expires_in=models.BigIntegerField(blank=True)
    class Meta:
        db_table=u'social_networks'
class Timezone(models.Model):
    zone_id=models.IntegerField()
    abbreviation=models.CharField(max_length=6)
    time_start=models.IntegerField()
    gmt_offset=models.IntegerField()
    dst=models.CharField(max_length=1)
    class Meta:
        db_table=u'timezone'
class Transactions(models.Model):
    transactions_id=models.BigIntegerField(primary_key=True)
    fk_users=models.ForeignKey(Users, db_column=u'fk_users')
    transactions_value=models.FloatField(null=True, blank=True)
    transactions_date=models.DateTimeField(null=True, blank=True)
    transactions_type=models.CharField(blank=True)
    fk_campaigns=models.ForeignKey(Campaigns, db_column=u'fk_campaigns')
    class Meta:
        db_table = u'transactions'
class UsersFollowsEvents(models.Model):
    users_follows_events_id=models.BigIntegerField(primary_key=True)
    users_follows_events_subscription_date=models.DateTimeField(null=True,blank=True)
    fk_users=models.ForeignKey(Users, db_column=u'fk_users')
    fk_events=models.ForeignKey(Events,db_column=u'fk_events',related_name='events_follows')
    class Meta:
        db_table=u'users_follows_events'
    def __unicode__(self):
        return '%s'%(self.fk_users)
class UsersUnfollowsEvents(models.Model):
    users_follows_events_id=models.BigIntegerField(primary_key=True)
    users_follows_events_unsubscribe_date=models.DateTimeField(null=True, blank=True)
    fk_users=models.ForeignKey(Users, db_column=u'fk_users')
    fk_events=models.ForeignKey(Events,db_column=u'fk_events')
    class Meta:
        db_table=u'users_unfollows_events'
    def __unicode__(self):
        return '%s'%(self.fk_users)    
class UsersHasFriends(models.Model):
    users_has_friends_id = models.BigIntegerField(primary_key=True)
    fk_user_from = models.ForeignKey(Users, db_column=u'fk_user_from')
    fk_user_to = models.ForeignKey(Users, db_column=u'fk_user_to')
    users_has_friends_delete = models.IntegerField(null=True, blank=True)
    users_has_friends_date = models.DateTimeField()
    class Meta:
        db_table = u'users_has_friends'
class UsersUploadMultimedias(models.Model):
    users_upload_media_id = models.BigIntegerField(primary_key=True)
    users_upload_media_date = models.DateTimeField(null=True, blank=True)
    fk_users = models.ForeignKey(Users, db_column=u'fk_users')
    fk_multimedias = models.ForeignKey(Multimedias, db_column=u'fk_multimedias')
    fk_events = models.ForeignKey(Events, db_column=u'fk_events')
    class Meta:
        db_table=u'users_upload_multimedias'        
class Comments(models.Model):
    #comments_id=models.BigIntegerField(primary_key=True)
    comments_id=models.AutoField(primary_key=True,db_column=u'comments_id')
    comments_value=models.CharField(max_length=300,blank=True)
    comments_date=models.DateTimeField(null=True,blank=True)
    class Meta:
        db_table=u'comments'
    def __unicode__(self):
        return '%d: %s : %s'%(self.comments_id,self.comments_value,self.comments_date)
    def get_json(self):
        return {'comments_id':self.comments_id}
class UsersWritesComments(models.Model):
    #users_writes_comments_id=models.BigIntegerField(primary_key=True)
    users_writes_comments_id=models.AutoField(primary_key=True,db_column=u'users_writes_comments_id')
    users_writes_comments_content=models.CharField(max_length=300,blank=True)
    #users_writes_comments_date = models.DateTimeField(null=True, blank=True)
    fk_users=models.ForeignKey(Users,db_column=u'fk_users',related_name='users_comments')
    fk_events=models.ForeignKey(Events,db_column=u'fk_events',related_name='events_comments')
    fk_comments=models.ForeignKey(Comments,db_column=u'fk_comments')
    users_writes_comments_delete=models.IntegerField(null=True,blank=True)
    class Meta:
        db_table=u'users_writes_comments'
    def __unicode__(self):
        return '%s'%(self.fk_comments)
    def get_json(self):
        return {
        'comment':self.users_writes_comments_content,
        'user':[{'id':b.users_id,'name':b.users_name} for b in self.user_set.all()]}
class Zone(models.Model):
    zone_id=models.IntegerField(primary_key=True)
    country_code=models.CharField(max_length=2)
    zone_name=models.CharField(max_length=35,blank=True)
    class Meta:
        db_table=u'zone'
class UsersHasHashtags(models.Model):
    users_has_hashtags_id=models.BigIntegerField(primary_key=True)
    fk_users=models.ForeignKey(Users, db_column=u'fk_users',related_name='hashtags')
    fk_hashtags=models.ForeignKey(Hashtags,db_column=u'fk_hashtags')
    class Meta:
        db_table = u'users_has_hashtags'
    def __unicode__(self):
        return '%s' % (self.fk_hashtags)
class UsersHideEvents(models.Model):
    users_hide_events_id=models.BigIntegerField(primary_key=True)
    fk_users=models.ForeignKey(Users,db_column=u'fk_users')
    fk_events=models.ForeignKey(Events,db_column=u'fk_events')
    class Meta:
        db_table = u'users_hide_events'
class Activities(models.Model):
    activities_id=models.AutoField(primary_key=True)
    user_id=models.BigIntegerField(db_column=u'fk_user')
    user_action_id=models.BigIntegerField(db_column=u'fk_user_action')
    action=models.BigIntegerField(db_column=u'fk_action')
    object=models.BigIntegerField(db_column=u'fk_object')
    activities_date=models.DateTimeField(null=False,blank=False)
    class Meta:
        db_table = u'activities'
class InvitationsMerryChristmas(models.Model):
    invitations_id=models.AutoField(primary_key=True)
    invitations_fb_ids=models.CharField(null=False,blank=False)
    invitations_msg=models.CharField(null=False,blank=False,max_length=500)
    class Meta:
        db_table=u'invitations_merry_christmas'
class EventsInvitations(models.Model):
    events_invitations_id=models.AutoField(primary_key=True)
    fk_users_from=models.BigIntegerField(db_column=u'fk_users_from')
    fk_users_to=models.CharField(null=False,blank=False,max_length=50)
    fk_events=models.BigIntegerField(db_column=u'fk_events')
    events_invitations_date=models.DateTimeField()
    class Meta:
        db_table=u'events_invitations'
class EventsAfter(models.Model):
    events_after_id=models.AutoField(primary_key=True)
    events_after_content=models.CharField(null=False,blank=False,max_length=500)
    events_after_type=models.CharField(null=False,blank=False,max_length=20)
    fk_events=models.BigIntegerField(db_column=u'fk_events')
    class Meta:
        db_table=u'events_after'