#from django.contrib import admin
#admin.autodiscover()
from django.conf.urls import url,patterns,include
from oclock.apps.db.models import Users,UsersType
from rest_framework import routers
from oclock.api.views import CreateUserViewSet,UsersViewSet,UsersTypeViewSet,EventViewSet,ResetPasswordViewSet,HashtagsViewSet,UsersWritesCommentsViewSet,InvitationsViewSet
from oclock.api.views import SharedEventsViewSet,UsersHideEventsViewSet,UsersHasHashtagsViewSet,NetworksTypeViewSet,SocialNetworksViewSet,UsersFollowsEventsViewSet,EventSpecialViewSet
from rest_framework.urlpatterns import format_suffix_patterns
router=routers.DefaultRouter()
#router = routers.SimpleRouter()
router.register(r'profiles',CreateUserViewSet,base_name="createuser")
router.register(r'users',UsersViewSet, base_name="users")
router.register(r'userstype',UsersTypeViewSet, base_name='userstype')
router.register(r'events',EventViewSet,base_name="events")
router.register(r'eventsspecial',EventSpecialViewSet,base_name="eventsspecial")
router.register(r'resetpassword',ResetPasswordViewSet, base_name='resetpassword')
router.register(r'usershashashtags',UsersHasHashtagsViewSet,base_name='usershashashtags')
router.register(r'hashtags',HashtagsViewSet,base_name='hashtags')
router.register(r'networkstype',NetworksTypeViewSet,base_name='networkstype')
router.register(r'socialnetworks',SocialNetworksViewSet,base_name='socialnetworks')
router.register(r'usersfollowevents',UsersFollowsEventsViewSet,base_name='usersfollowevents')
router.register(r'userswritescomments',UsersWritesCommentsViewSet,base_name='userswritescomments')
router.register(r'sharedevents',SharedEventsViewSet,base_name='sharedevents')
router.register(r'hide_event',UsersHideEventsViewSet,base_name='hide_event')
router.register(r'invitations',InvitationsViewSet,'invitations')
urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^', include('oclock.apps.base.urls')),
    #(r'^admin/', include('django.contrib.admin.urls')),
    #url(r'^user/admin/', include(admin.site.urls)),   
    url(r'^api-auth/', include('rest_framework.urls', namespace='oClock API')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2'))
)