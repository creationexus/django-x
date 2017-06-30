'''
Created on 28-05-2014
@author: carriagadad
'''
from django.conf.urls import url,patterns
from oclock.apps.base.services import event_details_api,event_details_str_api,get_events,get_events_migrate,event_details_str_api_21,get_activities,get_events_21,create_event_21,render_image,get_friends,check_event,stamp_all_images,like_event,events_read
from oclock.apps.base.views import main_page,event_details,create_user,get_more_data,detail_user,set_comment,embedded_event,panel,me,cr_ev,list_hot,list_ending,delete_events,list_following,terms_conditions,interface_old,enable_location,merry_christmas,delete_comments,admin_events_edit,stvalentine,crp,stvalentine_event
from oclock.apps.base.views import login_user,register_user,recovery_user,login_facebook,logout_user,follow_event,get_comments,share_event,inv_fr,cr_ev_tmp,hashtimes,list_hashtag,draft_events,privacy_policy,list_facebook_events,list_searching,list_finished,list_nearby,admin_events,admin_events_main,admin_events_delete,top
from oclock.apps.base.cron import cron_tasks,cron_list_high,cron_list_low
from oclock.apps.test.test import test_image
#from oclock.apps.networkssocial import twitter
urlpatterns=patterns('',
    #url(r'^$',main_page),
    url(r'^$',list_hot),
    url(r'^policy/privacy',privacy_policy),
    url(r'^policy/terms_conditions',terms_conditions),
    
    url(r'^hashtag/$',list_hashtag),
    url(r'^(?P<id>[a-z0-9-_]+)/$',event_details),
    #url(r'^events/m_da/(?P<id>\d+)/(?P<type>[a-z]+)',get_more_data),
    #url(r'^fo/e/(?P<id>\d+)/',follow_event),
    url(r'^em/ev/$',embedded_event),
    url(r'^in/new',cr_ev),
    #url(r'^u/in',login_user),
    url(r'^u/out',logout_user),
    url(r'^u/fb/in',login_facebook),
    url(r'^user/(?P<id>[a-zA-Z0-9-_.]+)/',detail_user),
    
    url(r'^admin/events/$',admin_events_main),
    url(r'^admin/events/(?P<c>\d+)/(?P<p>\d+)/',admin_events),
    url(r'^admin/events/edit/(?P<id>\d+)/$',admin_events_edit),
    url(r'^admin/events/delete/(?P<id>\d+)/$',admin_events_delete),
    
    url(r'^events/set_co/',set_comment),
    url(r'^events/new/',main_page),
    url(r'^events/ending/',list_ending),
    url(r'^events/following/',list_following),
    url(r'^events/fb_events/',list_facebook_events),
    url(r'^events/finished/',list_finished),
    url(r'^events/nearby/',list_nearby),
    url(r'^events/draft/',draft_events),
    #url(r'^events/hashtag/(?P<str>[a-zA-Z0-9-]+)/(?P<id>\d+)/',list_hashtag),
    url(r'^events/search/(?P<lst>[a-z]+)/',list_searching),
    
    url(r'^wishes/merry-christmas',merry_christmas),
    url(r'^special/stvalentine/',stvalentine_event),
    
    url(r'^clock/(?P<str>[a-zA-Z0-9-]+)/',interface_old),
    url(r'^event/delete/',delete_events),
    url(r'^event/image/(?P<id>\d+)/',render_image),
    url(r'^event/stvalentine',stvalentine),
    url(r'^comment/delete/',delete_comments),
    
    #url(r'^hashtimes/(?P<id>\d+)/',hashtimes),
    url(r'^api_v2/user/invitation/',inv_fr),
    url(r'^api_v2/events/$',get_events),
    url(r'^api_v2/events/read/',events_read),
    url(r'^api_v2/events/(?P<id>[a-z0-9-_]+)/$',event_details_str_api),
    url(r'^api_v2/events/id/(?P<id>\d+)/$',event_details_api),
    url(r'^api_v2/events/like/(?P<id>\d+)/',like_event),
    url(r'^api_v2/activities/',get_activities),
    url(r'^api_v2/events/share/(?P<id>\d+)/',share_event),
    url(r'^api_v2/userswritescomments/(?P<id>\d+)/(?P<pid>\d+)/',get_comments),
    url(r'^api_v2/friends/',get_friends),
    url(r'^api_v2/users/enable_location/',enable_location),
    
    url(r'^api_v2.1/migrate/$',get_events_migrate),
    url(r'^api_v2.1/events/$',get_events_21),
    url(r'^api_v2.1/events/create/',create_event_21),
    url(r'^api_v2.1/events/(?P<idx>[a-z0-9-_]+)/$',event_details_str_api_21),
    url(r'^api_v2.1/eventspecial/check/',check_event),
    
    url(r'^panel/n_ue',panel),
    url(r'^panel/top/(?P<n>\d+)',top),
    url(r'^udacity/crp/',crp),
    
    url(r'^util/stamp_all_images',stamp_all_images),
    #url(r'^cron/jHS-sjdIaj_jabc-quyUtqalKzM-jwyh8Ja-HqY',cron_list_low),
    #url(r'^cron/Uhagw37H-AAS_aUQhdII982-aAQqAh-W7kUjbXZ',cron_list_high),
    #url(r'^UyahFAtA5X-Xta6YZvxu-AzUhAjjJ-MM-98AQ_0',cron_tasks)
    url(r'^tests/upload_image',test_image),
    #url(r'^social/twitter',twitter)
)