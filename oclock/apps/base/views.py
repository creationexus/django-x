'''
Created on 28-05-2014
@author: carriagadad
'''
import os
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from google.appengine.api import users
from oclock.apps.db.models import Users,Events
from oclock.apps.mailing.services import Mandrill_Services
import urllib2
import json
import cgi
from django.conf import settings
import urllib
from rest_framework.response import Response
from rest_framework import status
from forms import LoginForm,CreateEvent,FriendInvitation,CreateEventChristmas,EditEvent,CreateEventValentine
from forms import Event,DeleteEvent,DraftEvent,UserEnableLocation,Activities,DeleteComment
import datetime
from django.utils.html import escape
import hashlib
from google.appengine.api import rdbms
from urlparse import urlparse
import itertools
import mimetools
import mimetypes
import time
from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import images
from django.views.decorators.cache import cache_page
import random
import logging
def mysqlconn():
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    return rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
def getCountryByIP(ip):
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
    c=conn.cursor()
    c.execute('SELECT cc FROM geoip_country WHERE INET_ATON(%s) BETWEEN start AND end LIMIT 1',(ip,))
    val=c.fetchone()
    if val is None:
        return None
    c.close()
    conn.close()
    return val[0]
def valid_token(t):
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
    c=conn.cursor()
    c.execute('SELECT user_id FROM oauth2_accesstoken WHERE token=%s AND TIMESTAMPDIFF(SECOND,NOW(),expires)>0',(t,))
    u_id=c.fetchone()
    c.close()
    conn.close()
    return u_id
def main_page(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        if str_token!='':
            u_id=None
            session_on=False
            user=None
            if str_token.strip()!='':
                u_id=valid_token(str_token)
            if u_id is not None:
                session_on=True
                try:
                    user=Users.objects.get(users_id=u_id[0])
                    try:
                        template_values = {
                            'nowt':time.strftime("%Y-%m-%dT%H:%M:%S"),
                            'user':user,
                            'session_on':session_on,
                            'users_id':request.session.get('users_id',0),
                            'users_name_id':request.session.get('users_name_id',''),
                            'users_name':request.session.get('users_name',' ').split(' ')[0],
                            'users_path_web_avatar':request.session.get('users_path_web_avatar','')
                        }
                        return render_to_response('oclock/main_page.html',template_values)
                    except urllib2.HTTPError, err:
                        if err.code == 404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                    else:
                        raise
                except Users.DoesNotExist:
                    return HttpResponseRedirect("/u/out")
            else:
                template_values={
                    'session_on':session_on,
                    'users_name':None,
                    'users_id':None,
                    'users_name_id':None,
                    'users_path_web_avatar':None
                }
                return render_to_response('oclock/main_page_public.html',template_values)
        else:
            template_values={'users_name':None}
            return render_to_response('oclock/main_page_public.html',template_values)
        return HttpResponse("e",status=401)
    return HttpResponse("e",status=401)
def event_details(request,id=None):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        user=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            try:
                user=Users.objects.get(users_id=u_id[0])
            except Users.DoesNotExist:
                return HttpResponseRedirect("/u/out")
            """if str_token is not None and str_token.strip() != '':"""
            """header=headers={
            'Authorization' : 'Bearer 923544fe76e51bc24530e6a86491b61e1452ecab',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            'Accept-Language': 'en-us',
            'Accept-Encoding': 'gzip, deflate, compress;q=0.9',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            }
            request = urllib2.Request("https://festive-ally-585.appspot.com/api/events/"+str(id),None,header)
            u = urllib2.urlopen(request)
            j_obj = u.read()
            j_obj = json.load(j) """
        try:
            req=urllib2.Request('https://festive-ally-585.appspot.com/api_v2/events/%s/'%str(id))
            if session_on:
                req.add_header('Authorization','Bearer %s'%str(str_token))
            res=urllib2.urlopen(req,timeout=60)
            j=res.read()
            j_obj=json.loads(j)
            m=random.choice(['magical','amazing','incredible'])
            
            template_values={'tso':time.strftime("%HH %MM %SS", time.gmtime(j_obj['events_seconds'])),'nowt':time.strftime("%Y-%m-%dT%H:%M:%S"),'ms_rnd':m,'user':user,'users_name_id':request.session.get('users_name_id',''),'event':j_obj,'session_on':session_on,'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'em_c':'<iframe style="width:400px;height:130px;" marginheight="0" marginwidth="0" noresize scrolling="No" frameborder="0" src="http://oclck.com/em/ev/?id='+j_obj['events_title_id']+'&w=400&h=130&c=746532">does not support iframe</iframe>'}
            res.close()
            return render_to_response('oclock/event_details.html',template_values)
        except urllib2.HTTPError, err:
            if err.code==404:
                return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
            return HttpResponse(err.code)
        except IndexError: 
            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        else:
            return HttpResponse("e")
        return HttpResponse("e")
    return HttpResponse("e")
def hashtimes(request,id=None):
    return HttpResponse('building...')
def sign_post(request):
    if request.method=='POST':
        guestbook_name = request.POST.get('guestbook_name')
        return HttpResponseRedirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))
    return HttpResponseRedirect('/')
def create_user(request):
    if request.method=='GET':
        template_values = {}
        #return direct_to_template(request, 'oclock/create_user.html', template_values)
        return render_to_response('oclock/create_user.html', template_values)
    if request.method=='POST':
        return HttpResponse('Its OK')
def login_user(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken',None)
        if str_token is not None and str_token.strip() != '':
            return HttpResponseRedirect("/")
        else:
            template_values = {'title':'Login User _ oClock'}
            return render_to_response('oclock/login_user.html', template_values)
    if request.method=='POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            u_email=form.cleaned_data['email']
            u_password=hashlib.sha1(str(form.cleaned_data['password'])).hexdigest()
            opener = urllib2.build_opener()
            opener.addheaders = [('', '')]
            try:
                data=urllib.urlencode({'client_id':'02770b9b0452d7e56a1d','client_secret':'0b671033626580921b56593440c3e387d0cb5ec6','grant_type':'password','users_email':str(u_email),'password':str(u_password)})
                res=opener.open('https://festive-ally-585.appspot.com/oauth2/access_token/',data,60)
                j=res.read()
                j_obj=json.loads(j)
                template_values = {'title':'Login User _ oClock','val':j_obj}
                max_age = 365*24*60*60  #one year
                expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
                #response.set_cookie("sessiontoken",j_obj['access_token'],max_age=max_age,expires=expires,domain=settings.SESSION_COOKIE_DOMAIN,secure=settings.SESSION_COOKIE_SECURE or None)
                request.session['sessiontoken']=j_obj['access_token']
                request.session['users_name']=escape(j_obj['users_name'])
                request.session.set_expiry(300) #5min
                return HttpResponseRedirect("/")
            except urllib2.HTTPError, err:
                if err.code==400:
                    template_values = {'title':'Login User _ oClock','status':'Incorrect email/password'}
                    return render_to_response('oclock/login_user.html', template_values)
                else:
                    template_values = {'title':'Login User _ oClock','status':'http'}
                    return render_to_response('oclock/login_user.html', template_values)
        else:
            template_values = {'title':'Login User _ oClock','status':form.errors}
            return render_to_response('oclock/login_user.html', template_values)
def logout_user(request):
    if request.session.get('sessiontoken',False):
        del request.session['sessiontoken']
    request.session.flush()
    return HttpResponseRedirect("/")
def register_user(request):
    if request.method == 'GET':
        template_values = {'title':'Register User _ oClock'}
        return render_to_response('oclock/test_get.html', template_values)
    if request.method == 'POST':
        u_email = request.POST.get('u_email', '')
        u_password = request.POST.get('u_password', '')
        return HttpResponse('%s %s'%(u_email,u_password))
def recovery_user(request):
    if request.method == 'GET':
        ms = Mandrill_Services()
        return HttpResponse(' tt %s ' % ms.send_mail())
def detail_user(request,id=None):
    if request.method == 'GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
        opener=urllib2.build_opener()
        opener.addheaders=[('Authorization', 'Bearer %s'%str(str_token))]
        try:
            res=opener.open('https://festive-ally-585.appspot.com/api/profiles/?users_name_id=%s'%str(id),None,60)
            j=res.read()
            j_obj=json.loads(j)
            template_values={'user':j_obj[0],'users_id':request.session.get('users_id',0),'session_on':session_on,'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/detail_user.html', template_values)
        except urllib2.HTTPError, err:
            if err.code==404:
                return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        except IndexError: 
            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        else:
            raise
    return HttpResponse("e")
def list_hot(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        session_on=False
        u_id=None
        user=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            try:
                user=Users.objects.get(users_id=u_id[0])
            except Users.DoesNotExist:
                return HttpResponseRedirect("/u/out")
        template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'nowt':time.strftime("%Y-%m-%dT%H:%M:%S"),'user':user}
        return render_to_response('oclock/hot_list.html', template_values)
    return HttpResponse("e")
def list_ending(request):
    if request.method == 'GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
        template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
        return render_to_response('oclock/ending_list.html', template_values)
    return HttpResponse("e")            #return HttpResponseRedirect("/u/fb/in?o="+request.get_full_path())
"""def set_cookie(response, name, value, domain=None, path="/", expires=None):
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain:
        cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))"""
def list_hashtag(request):
    if request.method=='GET':
        try:
            id=int(request.GET.get('id',None))
            str_token=request.session.get('sessiontoken','')
            u_id=None
            
            v_str=''
            session_on=False
            if str_token.strip()!='':
                u_id=valid_token(str_token)
            if u_id is not None:
                session_on=True
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c.execute('SELECT hashtags_value_str FROM hashtags WHERE hashtags_id=%s',(id,))
                value_str=c.fetchone()
                if value_str is not None:
                    v_str=value_str[0]
                c.close()
                conn.close()
            template_values={'id':id,'hashtags_name':str,'v_str':v_str,'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/hashtag_list.html', template_values)
        except:
            return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')
def list_following(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            template_values={'hashtags_name':str,'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/following_list.html',template_values)
        else:
            return HttpResponseRedirect('/u/fb/in/')
    return HttpResponse("e")
def list_facebook_events(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/facebook_events_list.html',template_values)
        else:
            return HttpResponseRedirect('/u/fb/in/')
        return HttpResponse('e')
    return HttpResponse('e')
def list_searching(request,lst=None):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        term=request.REQUEST.get('q','')
        if term=='':
            return HttpResponseRedirect('/')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
        template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'lst':lst,'search':term}
        return render_to_response('oclock/searching_list.html', template_values)
    return HttpResponse('e')
def list_finished(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
        template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
        return render_to_response('oclock/finished_list.html', template_values)
    return HttpResponse('e')
def list_nearby(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
        template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
        return render_to_response('oclock/nearby_list.html', template_values)
    return HttpResponse('e')
def login_facebook(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            return HttpResponseRedirect('/');
        else:
            verification_code=request.REQUEST.get("code",None)
            args=dict(client_id=settings.FACEBOOK_APP_ID,redirect_uri=request.build_absolute_uri())
            if verification_code is not None:
                args["client_secret"]=settings.FACEBOOK_APP_SECRET
                args["code"]=verification_code
                response=cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?"+urllib.urlencode(args)).read())
                if response.get('access_token',None) is None:
                    return HttpResponseRedirect('/');
                access_token=response["access_token"][-1]
                #profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+urllib.urlencode(dict(access_token=access_token))))
                """user = User(key_name=str(profile["id"]), id=str(profile["id"]),
                            name=profile["name"], access_token=access_token,
                            profile_url=profile["link"])"""
                """user.put()"""
                """set_cookie(response,"fb_user",str(profile["id"]),expires=time.time()+30*86400)"""
                #return HttpResponse(str(profile["id"])+'-'+str(profile["id"])+'-'+profile["name"]+'-'+access_token+'-'+profile["link"])
                opener=urllib2.build_opener()
                opener.addheaders = [('','')]
                try:
                    data=urllib.urlencode({'fk_networks_type':'/api/networkstype/1/','social_networks_token':access_token})
                    res=opener.open('https://festive-ally-585.appspot.com/api/socialnetworks/',data,60)
                    j=res.read()
                    j_obj=json.loads(j)
                    max_age=365*24*60*60  #one year
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
                    #response.set_cookie("sessiontoken",j_obj['access_token'],max_age=max_age,expires=expires,domain=settings.SESSION_COOKIE_DOMAIN,secure=settings.SESSION_COOKIE_SECURE or None)
                    request.session['sessiontoken']=j_obj['access_token']
                    request.session['users_name']=j_obj['users_name']
                    request.session['users_path_web_avatar']=j_obj['users_path_web_avatar']
                    request.session['users_id']=j_obj['users_id']
                    request.session['users_name_id']=j_obj['users_name_id']
                    request.session.set_expiry(864000) #10d
                    #return HttpResponse(request.get_full_path())
                    #return HttpResponse(request.build_absolute_uri(None))
                    #request.get_full_path()
                    #return HttpResponse(request.META.get('HTTP_REFERER',""))
                    if j_obj['is_new']=='0':
                        location=request.REQUEST.get("o","")+"#login"
                    else:
                        location=request.REQUEST.get("o","")+"#welcome"
                    res=HttpResponse(location,status=302)
                    res['Location']=location
                    conn=mysqlconn()
                    c=conn.cursor()
                    c.execute('UPDATE users SET users_device="web" WHERE users_id=%s',(j_obj['users_id'],))
                    conn.commit()
                    c.close()
                    conn.close()
                    return res
                except urllib2.HTTPError, err:
                    if err.code==400:
                        return HttpResponseRedirect('/');
                    else:
                        return HttpResponseRedirect('/');
                except ValueError:
                    logging.debug('EXCEPTION JSON!!!!')
                    logging.debug(str(j))
            else:
                args["scope"]="email,read_friendlists,user_interests,user_likes,user_events,user_birthday,publish_actions"
                return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?"+urllib.urlencode(args))
            return HttpResponse('e')
        return HttpResponse('e')
    return HttpResponse('e')
def get_more_data(request,id=None,type=None):
    if request.method=='GET':
        """str_token=request.session.get('sessiontoken',None)
        if str_token is not None and str_token.strip()!='':"""
        opener=urllib2.build_opener()
        try:
            res=opener.open('https://festive-ally-585.appspot.com/e/g_e?page=%s&t=%s'%(str(id),str(type)),None,60)
            j=res.read()
            j_obj=json.loads(j)
            if j_obj['next']!=None:
                template_values={'r':j_obj['results'],'n':'1'}
            else:
                template_values={'r':j_obj['results'],'n':'0'}
            return HttpResponse(json.dumps(template_values),content_type="application/json")
        except urllib2.HTTPError, err:
            if err.code == 404:
                return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        except IndexError: 
            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        else:
            return HttpResponse('')
        return HttpResponse('')
    else:
        return HttpResponse('')
    return HttpResponse('')

from io import BytesIO
from django.utils.encoding import smart_str, smart_unicode
class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary
    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return
    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body=fileHandle.read()
        if mimetype is None:
            mimetype=mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname,filename.encode("utf8"),mimetype,body))
        return
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts=[]
        part_boundary = '--' + self.boundary
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"'%name,
              '',
              value,
            ]
            for name,value in self.form_fields
            )
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name,filename,content_type,body in self.files
            )
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened=list(itertools.chain(*parts))
        flattened.append('--'+self.boundary+'--')
        flattened.append('')
        s=BytesIO()
        for element in flattened:
            s.write(smart_str(element))
            s.write('\r\n')
        return s.getvalue()
        #return '\r\n'.join(flattened)
def follow_event(request,id):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        #e_id=request.POST.get('e_id','')
        e_id=id
        if str_token.strip()!='' and e_id.strip()!='':
            #opener=urllib2.build_opener()
            #opener.addheaders=[('Authorization','Bearer %s'%str(str_token))]
            try:
                form=MultiPartForm()
                form.add_field('fk_events',str(e_id))
                body=str(form)
                #data=urllib.urlencode({'fk_events':str(e_id)})
                req=urllib2.Request('https://festive-ally-585.appspot.com/api/usersfollowevents/')
                req.add_header('Authorization','Bearer %s'%str(str_token))
                req.add_header('Content-type',form.get_content_type())
                req.add_header('Content-length',len(body))
                #req.add_data(data)
                req.add_data(body)
                res=urllib2.urlopen(req,timeout=60)
                #res=opener.open('https://festive-ally-585.appspot.com/api/usersfollowevents/',data,60)
                j=res.read()
                j_obj=json.loads(j)
                if j_obj['status']!=None and j_obj['status']=='follow':
                    template_values={'r':'f'}
                else:
                    template_values={'r':'n_f'}
                return HttpResponse(json.dumps(template_values),content_type="application/json")
            except urllib2.HTTPError,err:
                if err.code==404:
                    return HttpResponse('e1')
                return HttpResponse(str(err.code))
            except IndexError: 
                return HttpResponse('e2')
            return HttpResponse('e3')
        return HttpResponse('e4')
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        if str_token.strip()!='' and id.strip()!='':
            try:
                form=MultiPartForm()
                form.add_field('fk_events',str(id))
                body=str(form)
                req=urllib2.Request('https://festive-ally-585.appspot.com/api/usersfollowevents/')
                req.add_header('Authorization','Bearer %s'%str(str_token))
                req.add_header('Content-type',form.get_content_type())
                req.add_header('Content-length',len(body))
                req.add_data(body)
                res=urllib2.urlopen(req,timeout=60)
                ee=Events.objects.get(events_id=id)
                return HttpResponseRedirect("/%s"%ee.events_title_id)
            except urllib2.HTTPError,err:
                if err.code==404:
                    return HttpResponse('e1')
                return HttpResponse(str(err.code))
            except IndexError: 
                return HttpResponse('e2')
            return HttpResponse('e3')
        return HttpResponse('e4')
    return HttpResponse('e5')
def get_comments(request,id,pid):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        #e_id=request.POST.get('e_id','')
        #p_id=request.POST.get('p_id',0)
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if token.strip()!='':
            u_id=valid_token(token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            id=int(id)
            pid=int(pid)
            r={}
            d=[]
            c.execute('SELECT uwc.fk_comments,u.users_id,u.users_name_id,u.users_name,u.users_path_web_avatar,uwc.users_writes_comments_content,TIMESTAMPDIFF(SECOND,uwc.users_writes_comments_date,NOW()) AS seconds FROM users_writes_comments uwc LEFT JOIN users u ON u.users_id=uwc.fk_users WHERE fk_events=%s AND users_writes_comments_delete=0 ORDER BY users_writes_comments_id DESC LIMIT 100',(id,))
            for (fk_comments,users_id,users_name_id,users_name,users_path_web_avatar,users_writes_comments_content,seconds) in c:
                o={}
                o['comment_id']=fk_comments
                o['u_id']=users_id
                o['u_name_id']=users_name_id
                o['u_name']=users_name
                o['u_photo']=users_path_web_avatar
                o['msg']=users_writes_comments_content
                o['secs']=seconds
                d.append(o)
            r['r']=d
            r['n']=0
            r['token']=1
            c.close()
            conn.close()
            return HttpResponse(json.dumps(r),content_type="application/json")
        else:
            r={}
            r['r']=[]
            r['token']=0
            r['n']=0
            return HttpResponse(json.dumps(r),content_type="application/json")
    return HttpResponse('e')
def set_comment(request):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken',None)
        e_id=request.POST.get('e_id','')
        comm=request.POST.get('comm','')
        if str_token is not None and str_token.strip()!='' and e_id.strip()!='' and comm.strip()!='':
            try:
                form=MultiPartForm()
                form.add_field('fk_events',str(e_id))
                form.add_field('users_writes_comments_content',comm.strip())
                body=str(form)
                req=urllib2.Request('https://festive-ally-585.appspot.com/api/userswritescomments/')
                req.add_header('Authorization','Bearer %s'%str(str_token))
                req.add_header('Content-type',form.get_content_type())
                req.add_header('Content-length',len(body))
                req.add_data(body)
                res=urllib2.urlopen(req,timeout=60)
                j=res.read()
                j_obj=json.loads(j)
                if res.code==201:
                    template_values={'r':'w','c_c':j_obj['msg'],'c_u':j_obj['u_name_id'],'c_s':j_obj['secs']}
                else:
                    template_values={'r':'n_w'}
                res.close()
                return HttpResponse(json.dumps(template_values),content_type="application/json")
            except urllib2.HTTPError,err:
                if err.code==404:
                    return HttpResponse('e1')
                return HttpResponse(str(err.code))
            except IndexError: 
                return HttpResponse('e2')
            return HttpResponse('e3')
        return HttpResponse('e4')
    return HttpResponse('e5')
def embedded_event(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        user=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            try:
                user=Users.objects.get(users_id=u_id[0])
            except Users.DoesNotExist:
                return HttpResponseRedirect("/u/out")
        try:
            req=urllib2.Request('https://festive-ally-585.appspot.com/api_v2/events/%s/'%str(request.REQUEST.get("id",0)))
            if session_on:
                req.add_header('Authorization','Bearer %s'%str(str_token))
            res=urllib2.urlopen(req,timeout=60)
            j=res.read()
            j_obj=json.loads(j)
            w=request.REQUEST.get("w","200")
            h=request.REQUEST.get("h","300")
            bg=request.REQUEST.get("bg","00000")
            c=request.REQUEST.get("c","00000")
            template_values={'w':w,'h':h,'c':c,'bg':bg,'user':user,'users_name_id':request.session.get('users_name_id',''),'e':j_obj,'session_on':session_on,'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            res.close()
            return render_to_response('oclock/embedded_event.html',template_values)
        except urllib2.HTTPError, err:
            if err.code==404:
                return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
            return HttpResponse(err.code)
        except IndexError: 
            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
        else:
            return HttpResponse("e")
        return HttpResponse("e")
    return HttpResponse("e")
def get_p(p,c=30):
    r=[]
    r_by_p=c
    l_l=(p-1)*r_by_p
    r.append(l_l)
    #r.append(l_l+(r_by_p-1))
    r.append(r_by_p)
    return r
def share_event(request,id):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        if str_token.strip()!='' and id.strip()!='':
            try:
                form=MultiPartForm()
                form.add_field('fk_events',str(id))
                body=str(form)
                req=urllib2.Request('https://festive-ally-585.appspot.com/api/sharedevents/')
                req.add_header('Authorization','Bearer %s'%str(str_token))
                req.add_header('Content-type',form.get_content_type())
                req.add_header('Content-length',len(body))
                req.add_data(body)
                res=urllib2.urlopen(req,timeout=60)
                j=res.read()
                j_obj=json.loads(j)
                if j_obj['status']!=None and j_obj['status']=='shared':
                    template_values={'r':'s'}
                else:
                    template_values={'r':'n_s'}
                return HttpResponse(json.dumps(template_values),content_type="application/json")
            except urllib2.HTTPError,err:
                if err.code==404:
                    return HttpResponse('e1')
                return HttpResponse(str(err.code))
            except IndexError: 
                return HttpResponse('e2')
            return HttpResponse('e3')
        return HttpResponse('e4')
    return HttpResponse('e5')

def panel(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            if u_id[0] in [1,133,2812]:
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c.execute("SELECT COUNT(*) FROM users_follows_events")
                n_fo=c.fetchone()
                c.execute("SELECT COUNT(*) FROM users")
                n_ma=c.fetchone()
                c.execute("SELECT COUNT(*) FROM events")
                n_e=c.fetchone()
                c.execute("SELECT COUNT(*) FROM events WHERE events_delete=0")
                n_ev=c.fetchone()
                c.execute("select COUNT(*) from users WHERE users_date_joined < DATE_SUB(NOW(), INTERVAL 1 MONTH);")
                n_mb=c.fetchone()
                c.execute("select COUNT(*) from users WHERE users_date_joined < DATE_SUB(NOW(), INTERVAL 2 MONTH);")
                n_mc=c.fetchone()
                c.execute("select COUNT(*) from users WHERE users_date_joined < DATE_SUB(NOW(), INTERVAL 3 MONTH);")
                n_md=c.fetchone()
                fa=(n_ma[0]-n_mb[0])/float(n_mb[0])
                fb=(n_mb[0]-n_mc[0])/float(n_mc[0])
                fc=(n_mc[0]-n_md[0])/float(n_md[0])
                template_values={'n_u':n_ma[0],'n_e':n_e[0],'n_c':"%.2f"%((fa+fb+fc)/float(3)),'n_fo':n_fo[0],'n_ev':n_ev[0]}
                c.close()
                conn.close()
                return render_to_response('oclock/panel.html',template_values)
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            if u_id[0] in [1,133,2812]:
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c.execute('SELECT COUNT(*) FROM users')
                n_u=c.fetchone()
                c.execute('SELECT COUNT(*) FROM events')
                n_e=c.fetchone()
                template_values={'n_u':n_u[0],'n_e':n_e[0]}
                c.close()
                conn.close()
                return HttpResponse(json.dumps(template_values),content_type="application/json")
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def me(request):
    if request.method=='GET':
        return HttpResponse('me')
    return HttpResponse('e1')
def cr_ev(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            template_values={'users_name_id':request.session.get('users_name_id',' '),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'title':'','im_bg':'','type':'','dateq':'','hashtag':'','e_id':''}
            return render_to_response('oclock/create_event.html',template_values)
        return HttpResponseRedirect('/u/fb/in/')
    if request.method=='POST':
        #InMemoryUploadedFile
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            form=CreateEvent(request.POST,request.FILES)
            if form.is_valid():
                title=form.cleaned_data['tit']
                date=form.cleaned_data['dt']
                time=form.cleaned_data['tm']
                type=form.cleaned_data['tp']
                hsa=form.cleaned_data['hs1'].replace(',', '')
                hsb=form.cleaned_data['hs2'].replace(',', '')
                hsc=form.cleaned_data['hs3'].replace(',', '')
                lat=form.cleaned_data['lat']
                lon=form.cleaned_data['lon']
                country=form.cleaned_data['country']
                str_img=form.cleaned_data['str_img']
                hss=''
                if hsa.strip()!="":
                    hss+=hsa+","
                if hsb.strip()!="":
                    hss+=hsb+","
                if hsc.strip()!="":
                    hss+=hsc+","
                file_data=form.cleaned_data['fileselect']
                if file_data is None:
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title',title)
                        formm.add_field('events_type',str(type))
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags',hss[:-1])
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_img_str',str_img)
                        dt=datetime.datetime.combine(date,time)
                        if type==1:
                            formm.add_field('events_start',str(dt))#.strftime("%Y-%m-%d %H:%M:%S"))
                        elif type==2:
                            formm.add_field('events_finish',dt.strftime("%Y-%m-%d %H:%M:%S"))
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/events/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(j_obj['events_title_id'],status=201)
                    except urllib2.HTTPError, err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        return HttpResponse(err.read())
                    else:
                        return HttpResponse("e")
                elif file_data.content_type=='image/jpeg' or file_data.content_type=='image/png' or file_data.content_type=='image/bmp': 
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title',title)
                        formm.add_field('events_type',str(type))
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags',hss)
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_img_str',str_img)
                        dt=datetime.datetime.combine(date,time)
                        if type==1:
                            formm.add_field('events_start',str(dt))#.strftime("%Y-%m-%d %H:%M:%S"))
                        elif type==2:
                            formm.add_field('events_finish',dt.strftime("%Y-%m-%d %H:%M:%S"))
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        formm.add_file('events_image',file_data.name,file_data,file_data.content_type)
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/events/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(j_obj['events_title_id'],status=201)
                        
                        """dt=datetime.datetime.combine(date,time)
                        payload = {}
                        #payload['events_image']=request.POST['fileselect']
                        file_data=form.cleaned_data['fileselect']#request.POST['fileselect']
                        payload['events_image'] = MultipartParam('events_image',filename=file_data.name,
                                              filetype=file_data.content_type,
                                              filesize=file_data.size,
                                              fileobj=file_data)
                        payload['events_title']=title
                        payload['events_type']=str(type)
                        if type==1:
                            payload['events_start']=dt.strftime("%Y-%m-%d %H:%M:%S")
                        elif type==2:
                            payload['events_finish']=dt.strftime("%Y-%m-%d %H:%M:%S")
                        payload['events_skins']='skin1'
                        to_post=multipart_encode(payload)
                        send_url="https://festive-ally-585.appspot.com/api/events/"
                        result=urlfetch.fetch(url=send_url, payload="".join(to_post[0]), method=urlfetch.POST, headers={"Authorization": "Bearer %s"%str_token})#to_post[1])
                        
                        return HttpResponse(result.content,status=400)"""
                    except urllib2.HTTPError, err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        #return HttpResponse(err.code)
                        return HttpResponse(err.read())
                    else:
                        return HttpResponse("e")
                else:
                    return HttpResponse("e")
            else:
                return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
        return HttpResponse('e',status=400)
    return HttpResponse('e',status=401)
def inv_fr(request):
    if request.method=='GET':
        return HttpResponse('<>',status=200)
    if request.method=='POST':
        str_token=request.session.get('sessiontoken',None)
        if str_token is not None and str_token.strip()!='':
            form=FriendInvitation(request.POST,request.FILES)
            if form.is_valid():
                email=form.cleaned_data['email']
                try:
                    form=MultiPartForm()
                    form.add_field('email',email)
                    body=str(form)
                    req=urllib2.Request('https://festive-ally-585.appspot.com/api/invitations/')
                    req.add_header('Authorization','Bearer %s'%str(str_token))
                    req.add_header('Content-type',form.get_content_type())
                    req.add_header('Content-length',len(body))
                    req.add_data(body)
                    res=urllib2.urlopen(req,timeout=60)
                    j=res.read()
                    #j_obj=json.loads(j)
                    return HttpResponse(json.dumps({'sent':'ok'}),content_type="application/json")
                except urllib2.HTTPError,err:
                    if err.code==404:
                        return HttpResponse('e1')
                    return HttpResponse(err.read())
                except IndexError: 
                    return HttpResponse('e2')
                return HttpResponse('e3')
            return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
        return HttpResponse('e5')
    return HttpResponse('e6')
def cr_ev_tmp(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        if str_token.strip()!='':
            template_values={'users_name_id':request.session.get('users_name_id',' '),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/create_event_test.html',template_values)
        return HttpResponseRedirect('/u/fb/in/')
    if request.method=='POST':
        #InMemoryUploadedFile
        str_token=request.session.get('sessiontoken',None)
        if str_token is not None and str_token.strip() != '':
            form=CreateEvent(request.POST,request.FILES)
            if form.is_valid():
                title=form.cleaned_data['tit']
                date=form.cleaned_data['dt']
                time=form.cleaned_data['tm']
                type=form.cleaned_data['tp']
                hsa=form.cleaned_data['hs1']
                hsb=form.cleaned_data['hs2']
                hsc=form.cleaned_data['hs3']
                lat=form.cleaned_data['lat']
                lon=form.cleaned_data['lon']
                hss=''
                if hsa.strip()!="":
                    hss+=hsa+","
                if hsb.strip()!="":
                    hss+=hsb+","
                if hsc.strip()!="":
                    hss+=hsc+","
                file_data=form.cleaned_data['fileselect']
                if file_data is None:
                        formm=MultiPartForm()
                        formm.add_field('events_title',title)
                        formm.add_field('events_type',str(type))
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags',hss)
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        dt=datetime.datetime.combine(date,time)
                        if type==1:
                            formm.add_field('events_start',str(dt))#.strftime("%Y-%m-%d %H:%M:%S"))
                        elif type==2:
                            formm.add_field('events_finish',dt.strftime("%Y-%m-%d %H:%M:%S"))
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/events/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(j_obj['events_title_id'],status=201)  
                elif file_data.content_type=='image/jpeg' or file_data.content_type=='image/png': 
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title',title)
                        formm.add_field('events_type',str(type))
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags',hss)
                        dt=datetime.datetime.combine(date,time)
                        if type==1:
                            formm.add_field('events_start',str(dt))#.strftime("%Y-%m-%d %H:%M:%S"))
                        elif type==2:
                            formm.add_field('events_finish',dt.strftime("%Y-%m-%d %H:%M:%S"))
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        formm.add_file('events_image',file_data.name,file_data,file_data.content_type)
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/events/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(j_obj['events_title_id'],status=201)
                        
                    except urllib2.HTTPError, err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        #return HttpResponse(err.code)
                        return HttpResponse(err.read())
                    else:
                        return HttpResponse("e")
                else:
                    return HttpResponse("e")
            else:
                return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
        return HttpResponse('e',status=400)
    
def delete_events(request):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            form=DeleteEvent(request.POST)
            if form.is_valid():
                try:
                    #request=urllib2.Request("https://festive-ally-585.appspot.com/api/events/"+str(form.cleaned_data['id'])+"/",None)
                    req=urllib2.Request("https://festive-ally-585.appspot.com/api/events/"+str(form.cleaned_data['id'])+"/",None)
                    req.add_header('Authorization','Bearer %s'%str(str_token))
                    req.get_method=lambda:'DELETE'
                    u=urllib2.urlopen(req,timeout=180)
                    #j=u.read()
                    #j_obj=json.load(j)
                    return HttpResponse('ok')
                except urllib2.HTTPError,err:
                    if err.code==401:
                        return HttpResponse('e')
                    else:
                        return HttpResponse('e')
                return HttpResponse('e')
            return HttpResponse('e')
        return HttpResponse('e')
    return HttpResponse('e',status=401)
    
def delete_comments(request):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            form=DeleteComment(request.POST)
            if form.is_valid():
                try:
                    req=urllib2.Request("https://festive-ally-585.appspot.com/api/userswritescomments/"+str(form.cleaned_data['id'])+"/",None)
                    req.add_header('Authorization','Bearer %s'%str(str_token))
                    req.get_method=lambda:'DELETE'
                    u=urllib2.urlopen(req,timeout=60)
                    return HttpResponse('ok',status=200)
                except urllib2.HTTPError,err:
                    if err.code==401:
                        return HttpResponse('e',status=401)
                    else:
                        return HttpResponse('e',status=400)
                return HttpResponse('e',status=401)
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    else:
        return HttpResponse('e',status=401)

import base64

def draft_events(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar','')}
            return render_to_response('oclock/draft_list.html',template_values)
        else:
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/')
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        session_on=False
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            session_on=True
            form=DraftEvent(request.POST)
            if form.is_valid():
                if form.cleaned_data['dateq'] is None:
                    dateq=""
                else:
                    dateq=form.cleaned_data['dateq'].strftime("%Y-%m-%d")
                e_id=form.cleaned_data['e_id']
                
                #image=urllib.urlopen(form.cleaned_data['img_bg'])
                #image_64="data:image/jpeg;base64,%s"%base64.encodestring(image.read()).replace("\n","")
                #image_64="data:image/png;base64,%s"%urllib.quote(image.read().encode("base64").replace("\n",""))
                
                template_values={'session_on':session_on,'users_id':request.session.get('users_id',0),'users_name_id':request.session.get('users_name_id',''),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'title':form.cleaned_data['title'],'im_bg':form.cleaned_data['img_bg'],'dateq':dateq,'type':form.cleaned_data['type'],'hashtag':form.cleaned_data['hashtag'],'e_id':e_id}
                return render_to_response('oclock/create_event.html',template_values)
            else:
                return HttpResponseRedirect('/')
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')
def privacy_policy(request):
    if request.method=='GET':
        return render_to_response('oclock/policy/privacy_policy.html',{})
    return HttpResponse('')
def terms_conditions(request):
    if request.method=='GET':
        return render_to_response('oclock/policy/terms.html',{})
    return HttpResponse('')
def interface_old(request,str=None):
    return HttpResponseRedirect('/')
def enable_location(request):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ",'').strip()
        if len(str_token)<=1 and len(token)<=1:
            return HttpResponse(json.dumps({}),content_type="application/json")
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if token.strip()!='':
            u_id=valid_token(token)
        if u_id is not None:
            form=UserEnableLocation(request.POST)
            if form.is_valid():
                if form.cleaned_data['enable_location'] is None:
                    return HttpResponse(json.dumps({}),content_type="application/json")
                else:
                    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                    DATABASE_NAME='oclock'
                    USER_NAME='root'
                    conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
                    c=conn.cursor()
                    c.execute('UPDATE users SET users_is_location_enable=%s WHERE users_id=%s',(form.cleaned_data['enable_location'],u_id))
                    c.close()
                    conn.commit()
                    conn.close()
                    return HttpResponse(json.dumps({'status':'ok','enable_location':form.cleaned_data['enable_location']}),content_type="application/json")
                return HttpResponse('e',status=400)
            return HttpResponse('e',status=400)
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def merry_christmas(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            imgs_rnd=['http://storage.googleapis.com/oclock-images/flat_christmas_tree.png','http://storage.googleapis.com/oclock-images/Christmas-Tree-2014.png','http://storage.googleapis.com/oclock-images/jojojo.png','http://storage.googleapis.com/oclock-images/Merry-Christmas/Rudolph-Second.png','http://storage.googleapis.com/oclock-images/Merry-Christmas/Rudolph.png','http://storage.googleapis.com/oclock-images/Merry-Christmas/Santa-Second.png','http://storage.googleapis.com/oclock-images/Merry-Christmas/Santa.png']
            rnd=random.choice(imgs_rnd)
            try:
                user=Users.objects.get(users_id=u_id[0])
                template_values={'nowt':time.strftime("%Y-%m-%dT%H:%M:%S"),'user':user,'users_name_id':request.session.get('users_name_id',' '),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'im_bg':rnd,'imgs_rnd':imgs_rnd}
                return render_to_response('oclock/merry_christmas.html',template_values)
            except Users.DoesNotExist:
                return HttpResponse('e',status=401) 
        return HttpResponseRedirect('/u/fb/in/?o=/wishes/merry-christmas')
    if request.method=='POST':
        #InMemoryUploadedFile
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            form=CreateEventChristmas(request.POST,request.FILES)
            if form.is_valid():
                str_img=form.cleaned_data['str_img']
                lat=form.cleaned_data['lat']
                lon=form.cleaned_data['lon']
                friends=form.cleaned_data['friends']
                country=form.cleaned_data['country']
                file_data=form.cleaned_data['fileselect']
                msg=form.cleaned_data['msg']
                if file_data is None:
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title','My Christmas Wish')
                        formm.add_field('events_type','2')
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags','Wishes,Merry Christmas,2014')
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_fb_ids',friends)
                        formm.add_field('events_msg',msg)
                        formm.add_field('events_img_str',str_img)
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_finish','2014-12-25 00:00:00')
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/eventsspecial/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(json.dumps({'e_title_id':j_obj['events_title_id'],'e_image':j_obj['events_image']}),status=201)
                    except urllib2.HTTPError, err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        return HttpResponse(err.read())
                    else:
                        return HttpResponse("e")
                elif file_data.content_type=='image/jpeg' or file_data.content_type=='image/png' or file_data.content_type=='image/bmp': 
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title','My Christmas Wish')
                        formm.add_field('events_type','2')
                        formm.add_field('events_skins','skin1')
                        formm.add_field('hashtags','Wishes,Merry Christmas,2014')
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_fb_ids',friends)
                        formm.add_field('events_msg',msg)
                        formm.add_field('events_img_str',str_img)
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_finish','2014-12-25 00:00:00')
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        formm.add_file('events_image',file_data.name,file_data,file_data.content_type)
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/events/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(json.dumps({'e_title_id':j_obj['events_title_id'],'e_image':j_obj['events_image']}),status=201)
                        
                    except urllib2.HTTPError, err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        #return HttpResponse(err.code)
                        return HttpResponse(err.read())
                    else:
                        return HttpResponse("e")
                else:
                    return HttpResponse("e")
            else:
                return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
        return HttpResponse('e',status=400)
    return HttpResponse('e',status=401)
def admin_events_main(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM users where fk_users_type=2 AND users_id=%s',(u_id,))
            hp=csr.fetchone()
            csr.close()
            conn.close()
            if hp is not None:
                return HttpResponseRedirect('/admin/events/1000/1/')
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def admin_events(request,c,p):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM users where fk_users_type=2 AND users_id=%s',(u_id,))
            hp=csr.fetchone()
            pp=get_p(int(p),int(c))
            csr.execute('SELECT events_id,events_title,events_delete,events_sort,events_cc,IF(events_type=2,TIMESTAMPDIFF(SECOND,NOW(),events_finish),TIMESTAMPDIFF(SECOND,events_start,NOW())) as events_seconds,events_title_id FROM events ORDER BY events_id DESC LIMIT %s,%s',(pp[0],pp[1]))
            r=csr.fetchall()
            csr.close()
            conn.close()
            if hp is not None:
                if r is not None:
                    return render_to_response('oclock/admin_events.html',{'r':r})
                else:
                    return render_to_response('oclock/admin_events.html',{'r':[]})
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            return render_to_response('oclock/not_found.html',{})
def admin_events_edit(request,id):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM users where fk_users_type=2 AND users_id=%s',(u_id,))
            hp=csr.fetchone()
            csr.execute('SELECT * FROM events WHERE events_id=%s',(id,))
            ev=csr.fetchone()
            op={}
            csr.execute('SELECT * FROM country')
            op['']='Seleccione'
            for vrq in csr.fetchall():
                op[vrq[0]]=vrq[1]
            
            #op['CL']='Chile'
            #op['TR']='Turkia'
            #op['DK']='Dinamarca'
            #op['US']='USA'
            
            csr.close()
            conn.close()
            if hp is not None:
                if ev is not None:
                    return render_to_response('oclock/admin_events_edit.html',{'e':ev,'op':op})
                else:
                    return HttpResponse('')
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM users where fk_users_type=2 AND users_id=%s',(u_id,))
            hp=csr.fetchone()
            if hp is not None:
                form=EditEvent(request.POST)
                if form.is_valid():
                    e_title=form.cleaned_data['e_title']
                    e_sort=form.cleaned_data['e_sort']
                    e_cc=form.cleaned_data['e_cc']                
                    csr.execute('UPDATE events SET events_title=%s,events_sort=%s,events_cc=%s WHERE events_id=%s',(e_title,e_sort,e_cc,id))
                    csr.close()
                    conn.commit()
                    conn.close()
                    return HttpResponse('ok')
            csr.close()
            conn.close()
        return HttpResponse('e',status=401)
def admin_events_delete(request,id):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM users where fk_users_type=2 AND users_id=%s',(u_id,))
            hp=csr.fetchone()
            if hp is not None:                
                csr.execute('UPDATE events SET events_delete=1 WHERE events_id=%s',(id,))
                csr.close()
                conn.commit()
                conn.close()
                return HttpResponse('ok')
            csr.close()
            conn.close()
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def top(request,n):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            csr=conn.cursor()
            csr.execute('SELECT * FROM membership WHERE fk_roles=3 AND fk_users=%s',(u_id,))
            hp=csr.fetchone()
            if hp is not None:                
                csr.execute('SELECT u.users_name,u.users_email,COUNT(*) AS n_events,(SELECT COUNT(*) FROM users_follows_events ufe WHERE fk_users=u.users_id) AS n_follows,(SELECT COUNT(*) FROM users_writes_comments uwc WHERE uwc.fk_users=u.users_id AND uwc.users_writes_comments_delete=0) AS n_comments FROM events e LEFT JOIN users u ON u.users_id=e.fk_user_creator LEFT JOIN membership m ON m.fk_users=u.users_id WHERE m.fk_users is NULL GROUP BY e.fk_user_creator ORDER BY COUNT(*) DESC LIMIT %s',(n,))
                r=csr.fetchall()
                csr.close()
                conn.close()
                return render_to_response('oclock/panel_top.html',{'r':r,'n':n})
            csr.close()
            conn.close()
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def stvalentine(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            imgs_rnd=['https://storage.googleapis.com/oclock-images/valentine_stamp.png']
            rnd=random.choice(imgs_rnd)
            try:
                user=Users.objects.get(users_id=u_id[0])
                template_values={'nowt':time.strftime("%Y-%m-%dT%H:%M:%S"),'user':user,'users_name_id':request.session.get('users_name_id',' '),'users_name':request.session.get('users_name',' ').split(' ')[0],'users_path_web_avatar':request.session.get('users_path_web_avatar',''),'im_bg':rnd,'imgs_rnd':imgs_rnd}
                return render_to_response('oclock/stvalentine.html',template_values)
            except Users.DoesNotExist:
                return HttpResponse('e',status=401) 
        return HttpResponseRedirect('/u/fb/in/?o=/event/stvalentine/')
    
    if request.method=='POST':
        #InMemoryUploadedFile
        str_token=request.session.get('sessiontoken','')
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if u_id is not None:
            form=CreateEventValentine(request.POST,request.FILES)
            if form.is_valid():
                str_img=form.cleaned_data['str_img']
                lat=form.cleaned_data['lat']
                lon=form.cleaned_data['lon']
                friends=form.cleaned_data['friends']
                country=form.cleaned_data['country']
                file_data=form.cleaned_data['fileselect']
                msg=form.cleaned_data['msg']
                start=form.cleaned_data['start']
                if file_data is None:
                    """try:
                        formm=MultiPartForm()
                        formm.add_field('events_title','Our Valentine\'s Clock')
                        formm.add_field('events_type','1')
                        formm.add_field('events_skins','skin1')
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_fb_ids',friends)
                        formm.add_field('events_msg',msg)
                        formm.add_field('events_img_str',str_img if str_img!='' else 'https://storage.googleapis.com/oclock-static/9b1f1cc960855656f542d5d8d3faca99b58e8fd5.jpg')
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_start',start)
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/eventsspecial/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(json.dumps({'e_id':j_obj['events_id'],'e_secs':j_obj['events_seconds'],'e_title':j_obj['events_title'],'e_type':j_obj['events_type'],'e_title_id':j_obj['events_title_id'],'e_image':j_obj['events_image']}),status=201)
                    except urllib2.HTTPError,err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        return HttpResponse(err.read(),status=err.code)
                    else:
                        return HttpResponse("e")"""
                    return HttpResponse(json.dumps({'events_image':'Need Image'}),content_type="application/json",status=400)
                elif file_data.content_type=='image/jpeg' or file_data.content_type=='image/png' or file_data.content_type=='image/bmp': 
                    try:
                        formm=MultiPartForm()
                        formm.add_field('events_title','Our Valentine\'s Clock')
                        formm.add_field('events_type','1')
                        formm.add_field('events_skins','skin1')
                        formm.add_field('events_latitude',lat)
                        formm.add_field('events_longitude',lon)
                        formm.add_field('events_country',country)
                        formm.add_field('events_fb_ids',friends)
                        formm.add_field('events_msg',msg)
                        formm.add_field('events_img_str',str_img)
                        formm.add_field('events_ip',request.META.get('REMOTE_ADDR'))
                        formm.add_field('events_start',start)
                        #return HttpResponse(request.FILES['fileselect'].encode("utf8"))
                        formm.add_file('events_image',file_data.name,file_data,file_data.content_type)
                        body=str(formm)
                        req=urllib2.Request('https://festive-ally-585.appspot.com/api/eventsspecial/')
                        req.add_header('Authorization','Bearer %s'%str(str_token))
                        req.add_header('Content-type',formm.get_content_type())
                        req.add_header('Content-length',len(body))
                        req.add_data(body)
                        res=urllib2.urlopen(req,timeout=60)
                        j=res.read()
                        j_obj=json.loads(j)
                        return HttpResponse(json.dumps({'e_id':j_obj['events_id'],'e_secs':j_obj['events_seconds'],'e_title':j_obj['events_title'],'e_type':j_obj['events_type'],'e_title_id':j_obj['events_title_id'],'e_image':j_obj['events_image']}),status=201)
                        
                    except urllib2.HTTPError,err:
                        if err.code==404:
                            return render_to_response('oclock/not_found.html',{'users_name_id':request.session.get('users_name_id',None)})
                        #return HttpResponse(err.code)
                        return HttpResponse(err.read(),status=400)
                    else:
                        return HttpResponse("e",status=400)
                else:
                    return HttpResponse("e",status=400)
            else:
                return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def crp(request):
    return render_to_response('oclock/test/crp.html',{})
def stvalentine_event(request):
    if request.method=='GET':
        conn=mysqlconn()
        c=conn.cursor()
        c.execute('SELECT SUM(TIMESTAMPDIFF(SECOND,events_start,NOW())) from events where events_type_special like "love" and events_delete=0')
        seconds=c.fetchone()
        c.execute('SELECT 1000 / COUNT(*) FROM events WHERE events_type_special LIKE "love" AND events_delete=0')
        ms=c.fetchone()
        c.close()
        conn.close()
        return render_to_response('oclock/stvalentine_event.html',{'seconds':seconds[0],'ms':ms[0]})
    if request.method=='POST':
        conn=mysqlconn()
        c=conn.cursor()
        c.execute('SELECT events_image FROM events WHERE events_type_special like "love" AND events_delete=0 ORDER BY RAND() LIMIT 1')
        val=c.fetchone()
        c.close()
        conn.close()
        return HttpResponse(val[0])
    return HttpResponse('e',status=401)