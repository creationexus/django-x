'''
Created on 22-12-2014

@author: carriagadad
'''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from google.appengine.api import rdbms
import json
import datetime
from oclock.apps.db.models import Events,Activities as ActivitiesModel
from oclock.apps.base.forms import Activities,Event
from oclock.apps.db.datastore import Events as EventsStore,Users as UsersStore,UsersFollowsEvents as UsersFollowsEventsStore,UsersWritesComments as UsersWritesCommentsStore,EventsQueue
from google.appengine.ext import ndb
from oclock.apps.base.utilities import slugify_sp
import time
import urllib,urllib2,cStringIO
from google.appengine.datastore.datastore_query import Cursor
from oclock.apps.media.images import remote_image2,thumbnail_image,remote_to_img,images_stamp,create_img
from google.appengine.api import files
from pubnub.Pubnub import Pubnub
def notifsocket():
    return Pubnub('pub-c-4a7ce3d0-bcc6-4f50-94aa-5cf469d6182e','sub-c-56c8ca56-a255-11e4-8d46-02ee2ddab7fe','sec-c-OTc3NTZjY2QtMmMyOS00MTg4LWI3ZDAtZDk5MTc4NTA4OTg5',True)
def mysqlconn():
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    return rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
def notifAll(e_id,u_id,action):
    #user_id
    #user_action_id
    #action=3,
    #object
    #activities_date=datetime.now()
    CLOUDSQL_INSTANCE='festive-ally-585:oclock'
    DATABASE_NAME='oclock'
    USER_NAME='root'
    conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
    c=conn.cursor()
    creator=0
    pubnub=notifsocket()
    #creator
    c.execute('SELECT fk_user_creator FROM events e WHERE events_id=%s',(e_id,))
    for orq in c.fetchall():
        creator=orq[0]
        ActivitiesModel(user_id=orq[0],user_action_id=u_id,action=action,object=e_id,activities_date=datetime.datetime.now()).save(force_insert=True)
    #follow and comment
    c.execute('SELECT u.users_id FROM users u LEFT JOIN events e ON e.fk_user_creator=u.users_id WHERE u.users_id IN(SELECT ufe.fk_users FROM users_follows_events ufe WHERE ufe.fk_events=%s) OR u.users_id IN(SELECT uwc.fk_users FROM users_writes_comments uwc WHERE uwc.fk_events=%s AND uwc.users_writes_comments_delete=0) GROUP BY u.users_id',(e_id,e_id))
    for orq in c.fetchall():
        if creator==orq[0]:
            continue
        else:
            pubnub.publish({
                'channel':'userch_'+str(orq[0]),
                'message':{'user_id':str(orq[0])}
            })
            ActivitiesModel(user_id=orq[0],user_action_id=u_id,action=(action+1),object=e_id,activities_date=datetime.datetime.now()).save(force_insert=True)
    c.close()
    conn.close()
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
    if t.strip()!='':
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
    return None
def get_p(p,c=20):
    r=[]
    r_by_p=c
    l_l=(p-1)*r_by_p
    r.append(l_l)
    r.append(r_by_p)
    return r
def event_details_api(request,id=None):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        u_id=None
        if str_token=='' and token=='':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c_n=conn.cursor()
            c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.events_id=%s AND e.events_delete=0',(id,))
            ev=c.fetchone()
            if ev is None:
                return HttpResponse(json.dumps({}),content_type="application/json",status=404)
            else:
                d_t={}
                for x,z in enumerate(c.description):                            
                    if type(ev[x]) is datetime.datetime:
                        d_t[z[0]]=str(ev[x])
                    else:
                        if z[0]=="fk_user_creator":
                            tt={}
                            c_n.execute('SELECT users_id,users_lastname,users_name_id,users_firstname,users_middle_name,users_hashtags,users_name,users_path_web_avatar FROM users WHERE users_id=%s',(ev[x],))
                            for rr in c_n.fetchall():
                                for xx,zz in enumerate(c_n.description):
                                    if type(rr[xx]) is datetime.datetime:
                                        tt[zz[0]]=str(rr[xx])
                                    else:
                                        tt[zz[0]]=rr[xx]
                            d_t['fk_users']=tt
                        elif z[0]=="events_image" and ev[x] is None:
                            d_t[z[0]]='https://festive-ally-585.appspot.com/static/images/default.jpg'
                        elif z[0]=="hashtags":
                            c_n.execute('SELECT h.hashtags_id,h.hashtags_value,h.hashtags_value_str FROM events_has_hashtags ehh LEFT JOIN hashtags h ON ehh.fk_hashtags=h.hashtags_id WHERE ehh.fk_events=%s',(id,))
                            hsh=[]
                            for (hashtags_id,hashtags_value,hashtags_value_str) in c_n.fetchall():
                                ha={}
                                ha['hashtags_id']=hashtags_id
                                ha['hashtags_value']=hashtags_value
                                ha['hashtags_value_str']=hashtags_value_str
                                hsh.append(ha)
                            d_t['events_hashtags']=hsh
                        elif z[0]=="events_delete":
                            pass
                        elif z[0]=="events_enable":
                            pass
                        elif z[0]=="events_msg":
                            pass
                        elif z[0]=="events_fb_ids":
                            pass
                        elif z[0]=="events_id":
                            c_n.execute('select count(*) as count from users_follows_events where fk_events=%s',(ev[x],))
                            d_t['events_likes']=c_n.fetchone()[0]
                            c_n.execute('select count(*) as count from users_writes_comments where fk_events=%s AND users_writes_comments_delete=0',(ev[x],))
                            d_t['events_comments']=c_n.fetchone()[0]
                            d_t['events_id']=ev[x]
                        else:
                            d_t[z[0]]=ev[x]
                c.close()
                c_n.close()
                conn.close()
                return HttpResponse(json.dumps(d_t),content_type="application/json")
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
            c_n=conn.cursor()
            c_p=conn.cursor()
            c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds,IF(ufe.users_follows_events_id IS NULL,0,1) AS is_user_follow, IF(uwc.users_writes_comments_id IS NULL,0,1) AS is_user_comment FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id AND ufe.fk_users=%s LEFT JOIN users_writes_comments uwc ON uwc.fk_events=e.events_id AND uwc.fk_users=%s AND uwc.users_writes_comments_delete=0 WHERE e.events_id=%s AND e.events_delete=0 GROUP BY e.events_id',(u_id[0],u_id[0],id))
            ev=c.fetchone()
            if ev is None:
                return HttpResponse(json.dumps({}),content_type="application/json",status=404)
            else:
                d_t={}
                for x,z in enumerate(c.description):                            
                    if type(ev[x]) is datetime.datetime:
                        d_t[z[0]]=str(ev[x])
                    else:
                        if z[0]=="hashtags":
                            c_n.execute('SELECT h.hashtags_id,h.hashtags_value,h.hashtags_value_str FROM events_has_hashtags ehh LEFT JOIN hashtags h ON ehh.fk_hashtags=h.hashtags_id WHERE ehh.fk_events=%s',(id,))
                            hsh=[]
                            for (hashtags_id,hashtags_value,hashtags_value_str) in c_n.fetchall():
                                ha={}
                                ha['hashtags_id']=hashtags_id
                                ha['hashtags_value']=hashtags_value
                                ha['hashtags_value_str']=hashtags_value_str
                                hsh.append(ha)
                            d_t['events_hashtags']=hsh
                        elif z[0]=="events_image" and ev[x] is None:
                            d_t[z[0]]='https://festive-ally-585.appspot.com/static/images/default.jpg'
                        elif z[0]=="events_delete":
                            pass
                        elif z[0]=="events_enable":
                            pass
                        elif z[0]=="events_msg":
                            pass
                        elif z[0]=="events_fb_ids":
                            pass
                        elif z[0]=="fk_user_creator":
                            tt={}
                            c_n.execute('SELECT users_id,users_lastname,users_name_id,users_firstname,users_middle_name,users_hashtags,users_name,users_path_web_avatar from users where users_id=%s',(ev[x],))
                            for rr in c_n.fetchall():
                                for xx,zz in enumerate(c_n.description):
                                    if type(rr[xx]) is datetime.datetime:
                                        tt[zz[0]]=str(rr[xx])
                                    else:
                                        tt[zz[0]]=rr[xx]
                            d_t['fk_users']=tt
                        elif z[0]=="events_id":
                            c_n.execute('select count(*) as count from users_follows_events where fk_events=%s',(ev[x],))
                            d_t['events_likes']=c_n.fetchone()[0]
                            c_n.execute('select count(*) as count from users_writes_comments where fk_events=%s AND users_writes_comments_delete=0',(ev[x],))
                            d_t['events_comments']=c_n.fetchone()[0]
                            d_t['events_id']=ev[x]
                        else:
                            d_t[z[0]]=ev[x]
                if d_t['events_type_special'] is None:
                    c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(7,'en_us'))
                    lq=c_p.fetchone()
                    if lq is not None:
                        d_t['events_connector']="%s %s"%(d_t['events_type'],lq[0])
                elif d_t['events_type_special'] in ['wishes','love']:
                    c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(6,'en_us'))
                    lq=c_p.fetchone()
                    if lq is not None:
                        d_t['events_connector']="%s %s"%(d_t['events_type_special'],lq[0])
                else:
                    d_t['events_connector']=''
                d_t['events_after']=[]
                if d_t['events_seconds']<0:
                    c_n.execute('SELECT users_fb_id FROM users WHERE users_id=%s',(u_id[0],))
                    fb_id=c_n.fetchone()
                    if fb_id is not None:
                        c_n.execute('SELECT events_after_content,events_after_type,events_invitations_date FROM events e LEFT JOIN events_invitations ei ON ei.fk_events=e.events_id LEFT JOIN events_after ea ON ea.fk_events=ei.fk_events WHERE ei.fk_events=%s AND ei.fk_users_to=%s',(d_t['events_id'],fb_id[0]))
                        ih={}
                        ro=[]
                        for dd in c_n.fetchall():
                            ih['content']=dd[0]
                            ih['type']=dd[1]
                            ih['date']=str(dd[2])
                            ro.append(ih)
                        d_t['events_after']=ro
                c.close()
                c_n.close()
                c_p.close()
                conn.close()
                return HttpResponse(json.dumps(d_t),content_type="application/json")
        else:
            return HttpResponse(json.dumps({}),content_type="application/json")
    return HttpResponse("e",status=401)
def event_details_str_api(request,id=None):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        u_id=None
        if str_token=='' and token=='':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c_n=conn.cursor()
            c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds, TIMESTAMPDIFF(SECOND,e.events_date_creation,NOW()) AS events_date_creation FROM events e WHERE e.events_title_id=%s AND e.events_delete=0',(id,))
            ev=c.fetchone()
            if ev is None:
                return HttpResponse(json.dumps({}),content_type="application/json",status=404)
            else:
                d_t={}
                for x,z in enumerate(c.description):                            
                    if type(ev[x]) is datetime.datetime:
                        d_t[z[0]]=str(ev[x])
                    else:
                        if z[0]=="fk_user_creator":
                            tt={}
                            c_n.execute('SELECT users_id,users_lastname,users_name_id,users_firstname,users_middle_name,users_hashtags,users_name,users_path_web_avatar FROM users WHERE users_id=%s',(ev[x],))
                            for rr in c_n.fetchall():
                                for xx,zz in enumerate(c_n.description):
                                    if type(rr[xx]) is datetime.datetime:
                                        tt[zz[0]]=str(rr[xx])
                                    else:
                                        tt[zz[0]]=rr[xx]
                            d_t['fk_users']=tt
                        elif z[0]=="events_image" and ev[x] is None:
                            d_t[z[0]]='https://festive-ally-585.appspot.com/static/images/default.jpg'
                        elif z[0]=="hashtags":
                            c_n.execute('SELECT h.hashtags_id,h.hashtags_value,h.hashtags_value_str FROM events_has_hashtags ehh LEFT JOIN hashtags h ON ehh.fk_hashtags=h.hashtags_id WHERE ehh.fk_events=%s',(ev[0],))
                            hsh=[]
                            for (hashtags_id,hashtags_value,hashtags_value_str) in c_n.fetchall():
                                ha={}
                                ha['hashtags_id']=hashtags_id
                                ha['hashtags_value']=hashtags_value
                                ha['hashtags_value_str']=hashtags_value_str
                                hsh.append(ha)
                            d_t['events_hashtags']=hsh
                        elif z[0]=="events_delete":
                            pass
                        elif z[0]=="events_enable":
                            pass
                        elif z[0]=="events_msg":
                            pass
                        elif z[0]=="events_fb_ids":
                            pass
                        elif z[0]=="events_id":
                            c_n.execute('select count(*) as count from users_follows_events where fk_events=%s',(ev[x],))
                            d_t['events_likes']=c_n.fetchone()[0]
                            c_n.execute('select count(*) as count from users_writes_comments where fk_events=%s AND users_writes_comments_delete=0',(ev[x],))
                            d_t['events_comments']=c_n.fetchone()[0]
                            d_t['events_id']=ev[x]
                        else:
                            d_t[z[0]]=ev[x]                            
                c.close()
                c_n.close()
                conn.close()
                return HttpResponse(json.dumps(d_t),content_type="application/json")
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
            c_n=conn.cursor()
            c_p=conn.cursor()
            c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds,IF(ufe.users_follows_events_id IS NULL,0,1) AS is_user_follow, IF(uwc.users_writes_comments_id IS NULL,0,1) AS is_user_comment, TIMESTAMPDIFF(SECOND,e.events_date_creation,NOW()) AS events_date_creation FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id AND ufe.fk_users=%s LEFT JOIN users_writes_comments uwc ON uwc.fk_events=e.events_id AND uwc.fk_users=%s AND uwc.users_writes_comments_delete=0 WHERE e.events_title_id=%s AND e.events_delete=0 GROUP BY e.events_id',(u_id[0],u_id[0],id))
            ev=c.fetchone()
            if ev is None:
                return HttpResponse(json.dumps({}),content_type="application/json",status=404)
            else:
                d_t={}
                for x,z in enumerate(c.description):
                    if type(ev[x]) is datetime.datetime:
                        d_t[z[0]]=str(ev[x])
                    else:
                        if z[0]=="hashtags":
                            c_n.execute('SELECT h.hashtags_id,h.hashtags_value,h.hashtags_value_str FROM events_has_hashtags ehh LEFT JOIN hashtags h ON ehh.fk_hashtags=h.hashtags_id WHERE ehh.fk_events=%s',(ev[0],))
                            hsh=[]
                            for (hashtags_id,hashtags_value,hashtags_value_str) in c_n.fetchall():
                                ha={}
                                ha['hashtags_id']=hashtags_id
                                ha['hashtags_value']=hashtags_value
                                ha['hashtags_value_str']=hashtags_value_str
                                hsh.append(ha)
                            d_t['events_hashtags']=hsh
                        elif z[0]=="events_image" and ev[x] is None:
                            d_t[z[0]]='https://festive-ally-585.appspot.com/static/images/default.jpg'
                        elif z[0]=="events_delete":
                            pass
                        elif z[0]=="events_enable":
                            pass
                        elif z[0]=="events_msg":
                            pass
                        elif z[0]=="events_fb_ids":
                            pass
                        elif z[0]=="fk_user_creator":
                            tt={}
                            c_n.execute('SELECT users_id,users_lastname,users_name_id,users_firstname,users_middle_name,users_hashtags,users_name,users_path_web_avatar from users where users_id=%s',(ev[x],))
                            for rr in c_n.fetchall():
                                for xx,zz in enumerate(c_n.description):
                                    if type(rr[xx]) is datetime.datetime:
                                        tt[zz[0]]=str(rr[xx])
                                    else:
                                        tt[zz[0]]=rr[xx]
                            d_t['fk_users']=tt
                        elif z[0]=="events_id":
                            c_n.execute('select count(*) as count from users_follows_events where fk_events=%s',(ev[x],))
                            d_t['events_likes']=c_n.fetchone()[0]
                            c_n.execute('select count(*) as count from users_writes_comments where fk_events=%s AND users_writes_comments_delete=0',(ev[x],))
                            d_t['events_comments']=c_n.fetchone()[0]
                            d_t['events_id']=ev[x]
                        else:
                            d_t[z[0]]=ev[x]
                if d_t['events_type_special'] is None:
                    c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(7,'en_us'))
                    lq=c_p.fetchone()
                    if lq is not None:
                        d_t['events_connector']="%s %s"%(d_t['events_type'],lq[0])
                elif d_t['events_type_special'] in ['wishes','love']:
                    c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(6,'en_us'))
                    lq=c_p.fetchone()
                    if lq is not None:
                        d_t['events_connector']="%s %s"%(d_t['events_type_special'],lq[0])
                else:
                    d_t['events_connector']=''
                d_t['events_after']=[]
                if d_t['events_seconds']<0:
                    c_n.execute('SELECT users_fb_id FROM users WHERE users_id=%s',(u_id[0],))
                    fb_id=c_n.fetchone()
                    if fb_id is not None:
                        c_n.execute('SELECT events_after_content,events_after_type,events_invitations_date FROM events e LEFT JOIN events_invitations ei ON ei.fk_events=e.events_id LEFT JOIN events_after ea ON ea.fk_events=ei.fk_events WHERE ei.fk_events=%s AND ei.fk_users_to=%s',(d_t['events_id'],fb_id[0]))
                        ih={}
                        ro=[]
                        for dd in c_n.fetchall():
                            ih['content']=dd[0]
                            ih['type']=dd[1]
                            ih['date']=str(dd[2])
                            ro.append(ih)
                        d_t['events_after']=ro
                c.close()
                c_n.close()
                c_p.close()
                conn.close()
                return HttpResponse(json.dumps(d_t),content_type="application/json")
        else:
            return HttpResponse(json.dumps({}),content_type="application/json")
    return HttpResponse("e")
def get_events(request):
    if request.method=='POST':
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        str_token=request.session.get('sessiontoken','')
        form=Event(request.POST)
        if form.is_valid():
            types=['me','user','new','hot','ending','hashtag','following','draft','facebook','finished','nearby']
            p=form.cleaned_data['page']
            t=form.cleaned_data['type']
            id=form.cleaned_data['id']
            img_size=form.cleaned_data['img_size']
            search=slugify_sp(form.cleaned_data['search'])
            device=form.cleaned_data['device']
            ##LIMPIAR search (ESCAPAR)
            if (t=="me" or t=="following" or t=='draft' or t=='facebook') and str_token=='' and token=='':
                return HttpResponse(json.dumps({}),content_type="application/json")
            u_id=None
            res=[]
            d={}
            u_id=0
            p=int(p)
            id=int(id)
            n_r=0
            country=''
            if img_size is not None:
                if img_size>1000:
                    img_size=1000
            else:
                img_size=500
            if p>0 and id>=0 and (t in types):
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                nn=get_p(p)
                c=conn.cursor()
                c_n=conn.cursor()
                c_p=conn.cursor()
                if search is not None:
                    search_str="%"+search+"%"
                else: 
                    search_str=""
                if device is None:
                    device=1
                if t=="new":
                    if device==0:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC',(search_str))
                    else:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC LIMIT %s, %s',(search_str,nn[0],nn[1]))
                elif t=='me' or t=='following' or t=='draft' or t=='facebook':
                    if str_token.strip()!='':
                        u_id=valid_token(str_token)
                    if token.strip()!='':
                        u_id=valid_token(token)
                    if u_id is not None:
                        if t=="me":
                            if device==0:
                                c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_id DESC',(u_id[0],search_str))
                            else:
                                c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_id DESC LIMIT %s, %s',(u_id[0],search_str,nn[0],nn[1]))
                        elif t=="following":
                            if device==0:
                                c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id WHERE ufe.fk_users=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC',(u_id[0],search_str))
                            else:
                                c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id WHERE ufe.fk_users=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC LIMIT %s, %s',(u_id[0],search_str,nn[0],nn[1]))
                        elif t=="draft":
                            c.execute('SELECT e.events_id,e.events_title,e.events_description,e.events_latitude,e.events_longitude,CASE e.events_id WHEN 1 THEN DATE_FORMAT(u.users_birthday,CONCAT(IF(MONTH(u.users_birthday)>=MONTH(NOW()) AND DAY(u.users_birthday)>=DAY(NOW()),YEAR(NOW()),YEAR(NOW())+1),"-%%m-%%d %%T")) ELSE NULL END as events_finish,CASE e.events_id WHEN 2 THEN u.users_birthday ELSE NULL END as events_start,CASE e.events_id  WHEN 1 THEN "countdown" WHEN 2 THEN "timer" ELSE NULL END as events_type,CASE e.events_id WHEN 1 THEN u.users_path_web_avatar WHEN 2 THEN u.users_path_web_avatar ELSE NULL END AS events_image, %s as fk_user_creator,e.events_enable,e.events_delete,e.events_language,e.events_country,e.events_velocity,e.events_level,e.events_title_id,e.events_skins,e.events_fb_event_id,e.events_date_creation,e.hashtags,CASE e.events_id WHEN 1 THEN TIMESTAMPDIFF(SECOND,NOW(),DATE_FORMAT(u.users_birthday,CONCAT(IF(MONTH(u.users_birthday)>=MONTH(NOW()) AND DAY(u.users_birthday)>=DAY(NOW()),YEAR(NOW()),YEAR(NOW())+1),"-%%m-%%d %%T"))) WHEN 2 THEN TIMESTAMPDIFF(SECOND,u.users_birthday,NOW()) ELSE NULL END as events_seconds,e.events_type_special FROM events_draft e LEFT JOIN users u ON u.users_id=%s LIMIT %s, %s',(u_id[0],u_id[0],nn[0],nn[1]))
                        elif t=='facebook':
                            c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN events_from_facebook eff ON eff.fk_events=e.events_id WHERE eff.fk_users=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC LIMIT %s,%s',(u_id[0],search_str,nn[0],nn[1]))
                elif t=="user":
                    if device==0:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC',(id,search_str))
                    else:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_fixed DESC,e.events_id DESC LIMIT %s, %s',(id,search_str,nn[0],nn[1]))
                elif t=="hot":
                    if device==0:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id WHERE e.events_sort>0 AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) GROUP BY e.events_id ORDER BY e.events_sort DESC',(search_str))
                    else:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id WHERE e.events_sort>0 AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) GROUP BY e.events_id ORDER BY e.events_sort DESC LIMIT %s, %s',(search_str,nn[0],nn[1]))
                elif t=="ending":
                    if device==0:
                        #c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events_medium e WHERE e.events_delete=0 AND e.events_title LIKE %s ORDER BY e.events_id DESC',(search_str))
                        c.execute('SELECT e.*,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) AS events_seconds FROM events e WHERE e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0 AND e.events_title LIKE %s AND e.events_delete=0 ORDER BY TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)',(search_str,))
                    else:
                        #c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events_medium e WHERE e.events_delete=0 AND e.events_title LIKE %s ORDER BY e.events_id DESC LIMIT %s, %s',(search_str,nn[0],nn[1]))
                        c.execute('SELECT e.*,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) AS events_seconds FROM events e WHERE e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0 AND e.events_title LIKE %s AND e.events_delete=0 ORDER BY TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) LIMIT %s, %s',(search_str,nn[0],nn[1]))
                elif t=="hashtag":
                    if device==0:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN events_has_hashtags ehh ON ehh.fk_events=e.events_id WHERE ehh.fk_hashtags=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) GROUP BY ehh.fk_events',(id,search_str))
                    else:
                        c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e LEFT JOIN events_has_hashtags ehh ON ehh.fk_events=e.events_id WHERE ehh.fk_hashtags=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) GROUP BY ehh.fk_events LIMIT %s,%s',(id,search_str,nn[0],nn[1]))
                elif t=='finished':
                    c.execute('SELECT e.*,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) AS events_seconds FROM events e WHERE e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)<0 AND e.events_title LIKE %s AND e.events_delete=0 ORDER BY TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) DESC LIMIT %s,%s',(search_str,nn[0],nn[1]))
                elif t=='nearby':
                    country=getCountryByIP(request.META.get('REMOTE_ADDR'))
                    c.execute('SELECT e.*,IF(e.events_type=2,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish),TIMESTAMPDIFF(SECOND,e.events_start,NOW())) as events_seconds FROM events e WHERE e.events_title LIKE %s AND e.events_delete=0 AND (events_cc=%s OR events_fixed=1) AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) ORDER BY e.events_id DESC LIMIT %s,%s',(search_str,country,nn[0],nn[1]))
                n_r=c.rowcount
                if n_r>0:
                    cx=0
                    d['count']=n_r
                    if device>0:
                        nn=get_p(p+1)
                        if t=="new":
                            c_n.execute('SELECT e.* FROM events e WHERE e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s, %s',(search_str,nn[0],nn[1]))
                        elif t=="me":
                            c_n.execute('SELECT e.* FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s, %s',(u_id[0],search_str,nn[0],nn[1]))
                        elif t=="user":
                            c_n.execute('SELECT e.* FROM events e WHERE e.fk_user_creator=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s, %s',(id,search_str,nn[0],nn[1]))
                        elif t=="hot":
                            c_n.execute('SELECT e.* FROM events e WHERE e.events_sort>0 AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s, %s',(search_str,nn[0],nn[1]))
                        elif t=="ending":
                            #c_n.execute('SELECT e.* FROM events_medium e WHERE e.events_delete=0 AND e.events_title LIKE %s LIMIT %s, %s',(search_str,nn[0],nn[1]))
                            c_n.execute('SELECT e.*,TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) AS events_seconds FROM events e WHERE e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0 AND e.events_title LIKE %s AND e.events_delete=0 ORDER BY TIMESTAMPDIFF(SECOND,NOW(),e.events_finish) LIMIT %s, %s',(search_str,nn[0],nn[1]))
                        elif t=="hashtag":
                            c_n.execute('SELECT e.* FROM events e LEFT JOIN events_has_hashtags ehh ON ehh.fk_events=e.events_id WHERE ehh.fk_hashtags=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) GROUP BY ehh.fk_events LIMIT %s, %s',(id,search_str,nn[0],nn[1]))
                        elif t=="following":
                            c_n.execute('SELECT e.* FROM events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id WHERE ufe.fk_users=%s AND e.events_delete=0 AND e.events_title LIKE %s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s, %s',(u_id[0],search_str,nn[0],nn[1]))
                        elif t=="draft":
                            c_n.execute('SELECT e.* FROM events_draft e LIMIT %s, %s',(nn[0],nn[1]))
                        elif t=='facebook':
                            c_n.execute('SELECT e.* FROM events e LEFT JOIN events_from_facebook eff ON eff.fk_events=e.events_id WHERE eff.fk_users=%s AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s,%s',(u_id[0],nn[0],nn[1]))
                        elif t=='finished':
                            c_n.execute('SELECT e.* FROM events e WHERE e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)<0 AND e.events_title LIKE %s AND e.events_delete=0 LIMIT %s,%s',(search_str,nn[0],nn[1]))
                        elif t=='nearby':
                            c_n.execute('SELECT e.* FROM events e WHERE e.events_title LIKE %s AND e.events_delete=0 AND (events_cc=%s OR events_fixed=1) AND ((e.events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),e.events_finish)>0) OR (e.events_type=1)) LIMIT %s,%s',(search_str,country,nn[0],nn[1]))
                        cx=c_n.rowcount
                    if cx>0 and device>0:
                        d['n']='1'
                    else:
                        d['n']='0'
                    d['previous']=None
                    for r in c.fetchall():
                        d_t={}
                        e_id=0
                        for x,z in enumerate(c.description):
                            if type(r[x]) is datetime.datetime:
                                d_t[z[0]]=str(r[x])
                            else:
                                if z[0]=="fk_user_creator":
                                    tt={}
                                    c_n.execute("select users_id,users_lastname,users_name_id,users_firstname,users_middle_name,users_hashtags,users_name,users_path_web_avatar from users where users_id=%s"%r[x])
                                    for rr in c_n.fetchall():
                                        for xx,zz in enumerate(c_n.description):
                                            if type(rr[xx]) is datetime.datetime:
                                                tt[zz[0]]=str(rr[xx])
                                            else:
                                                tt[zz[0]]=rr[xx]
                                    d_t['fk_users']=tt
                                elif z[0]=="events_image" and r[x] is None:
                                    d_t[z[0]]='https://festive-ally-585.appspot.com/static/images/default.jpg'
                                elif z[0]=="events_image" and r[x] is not None:
                                    d_t[z[0]]=r[x]#d_t[z[0]]=r[x][0:-3]+str(img_size)
                                elif t!="draft" and z[0]=="events_id" and r[x]!=None:
                                    c_n.execute("SELECT COUNT(*) as count from users_follows_events where fk_events=%s",(r[x],))
                                    d_t['events_like']=c_n.fetchone()[0]
                                    c_n.execute("SELECT COUNT(*) as count from users_writes_comments where fk_events=%s",(r[x],))
                                    d_t['events_comment']=c_n.fetchone()[0]
                                    c_n.execute('SELECT h.hashtags_id,h.hashtags_value,h.hashtags_value_str FROM events_has_hashtags ehh LEFT JOIN hashtags h ON ehh.fk_hashtags=h.hashtags_id WHERE ehh.fk_events=%s',(r[x],))
                                    hsh=[]
                                    for (hashtags_id,hashtags_value,hashtags_value_str) in c_n.fetchall():
                                        ha={}
                                        ha['hashtags_id']=hashtags_id
                                        ha['hashtags_value']=hashtags_value
                                        ha['hashtags_value_str']=hashtags_value_str
                                        hsh.append(ha)
                                    d_t['events_hashtags']=hsh
                                    d_t['events_id']=r[x]
                                elif z[0]=="events_delete":
                                    pass
                                elif z[0]=="events_enable":
                                    pass
                                elif z[0]=="hashtags" and t!="draft":
                                    pass
                                elif z[0]=="events_msg":
                                    pass
                                elif z[0]=="events_fb_ids":
                                    pass
                                else:
                                    d_t[z[0]]=r[x]

                        if d_t['events_type_special'] is None:
                            c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(7,'en_us'))
                            lq=c_p.fetchone()
                            if lq is not None:
                                d_t['events_connector']="%s %s"%(d_t['events_type'],lq[0])
                        elif d_t['events_type_special']=='wishes':
                            c_p.execute('SELECT l.language_value FROM language l LEFT JOIN language_type lt ON lt.language_type_id=l.fk_language_type where l.language_action=%s AND language_type_value=%s',(6,'en_us'))
                            lq=c_p.fetchone()
                            if lq is not None:
                                d_t['events_connector']="%s %s"%(d_t['events_type_special'],lq[0])
                        else:
                            d_t['events_connector']=''
                        d_t['events_after']=[]
                        if u_id is not None and u_id>0:
                            if d_t['events_seconds']<0:
                                c_n.execute('SELECT users_fb_id FROM users WHERE users_id=%s',(u_id[0],))
                                fb_id=c_n.fetchone()
                                if fb_id is not None:
                                    c_n.execute('SELECT events_after_content,events_after_type,events_invitations_date FROM events e LEFT JOIN events_invitations ei ON ei.fk_events=e.events_id LEFT JOIN events_after ea ON ea.fk_events=ei.fk_events WHERE ei.fk_events=%s AND ei.fk_users_to=%s',(d_t['events_id'],fb_id[0]))
                                    ih={}
                                    ro=[]
                                    for dd in c_n.fetchall():
                                        ih['content']=dd[0]
                                        ih['type']=dd[1]
                                        ih['date']=str(dd[2])
                                        ro.append(ih)
                                    d_t['events_after']=ro
                        res.append(d_t)
                    d['r']=res
                else:
                    d['r']=[]
                    d['count']=0
                    d['n']='0'
                    d['previous']=None
                c.close()
                c_n.close()
                c_p.close()
                conn.close()
                return HttpResponse(json.dumps(d),content_type="application/json")
            return HttpResponse(json.dumps({}),content_type="application/json")
        else:
            return HttpResponse(json.dumps(form.errors),content_type="application/json")
    return HttpResponse(json.dumps({}),content_type="application/json")
def get_activities(request):
    if request.method=='POST':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        form=Activities(request.POST)
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if token.strip()!='':
            u_id=valid_token(token)
        if u_id is not None:
            if form.is_valid():
                CLOUDSQL_INSTANCE='festive-ally-585:oclock'
                DATABASE_NAME='oclock'
                USER_NAME='root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c.execute('SELECT u.users_name,u.users_name_id,u.users_path_web_avatar,l.language_value,e.events_type,TIMESTAMPDIFF(SECOND,a.activities_date,NOW()) as activities_seconds,e.events_title_id,e.events_id,a.activities_read FROM activities a LEFT JOIN language l ON l.language_action=a.fk_action LEFT JOIN users u ON u.users_id=a.fk_user_action LEFT JOIN events e ON e.events_id=a.fk_object WHERE a.fk_user=%s AND (a.fk_user_action<>%s OR a.fk_user_action IS NULL) ORDER BY activities_seconds ASC LIMIT 50',(u_id,u_id))
                r={}
                d=[]
                for (users_name,users_name_id,users_path_web_avatar,language_value,events_type,activities_seconds,events_title_id,events_id,activities_read) in c.fetchall():
                    o={}
                    o['users_name']=users_name
                    o['users_name_id']=users_name_id
                    o['users_image']=users_path_web_avatar
                    o['language_value']=language_value
                    o['events_type']=events_type
                    o['activities_seconds']=activities_seconds
                    o['events_title_id']=events_title_id
                    o['events_id']=events_id
                    o['activities_read']=activities_read
                    d.append(o)
                r['r']=d
                r['n']=0
                c.close()
                conn.close()
                return HttpResponse(json.dumps(r),content_type="application/json")
            else:
                return HttpResponse('e',status=400)
        else:
            return HttpResponse('e',status=401)
        return HttpResponse('e',status=401)
    return HttpResponse('e',status=401)
def get_events_migrate(request):
    if request.method=='GET':
        action=request.REQUEST.get('action','1')
        page=int(request.REQUEST.get('page','1'))
        if action=='1':
            ndb.delete_multi(
                EventsStore.query().iter(keys_only=True)
            )
            ndb.delete_multi(
                UsersStore.query().iter(keys_only=True)
            )
            ndb.delete_multi(
                UsersFollowsEventsStore.query().iter(keys_only=True)
            )
            ndb.delete_multi(
                UsersWritesCommentsStore.query().iter(keys_only=True)
            )
            return HttpResponse('')
        elif action=='2':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            pp=get_p(page,500)
            c.execute('SELECT events_id,events_title,events_description,events_latitude,events_longitude,events_start,events_finish,events_type,fk_user_creator,events_enable,events_delete,events_language,events_country,events_velocity,events_image,events_level,events_title_id,events_skins,events_fb_event_id,hashtags,events_cc,events_ip,events_fb_ids,events_msg,events_img_str,events_sort FROM events LIMIT %s,%s',(pp[0],pp[1]))
            for e in c.fetchall():
                ev=EventsStore(events_id=str(e[0]),
                events_title=e[1],
                events_description=e[2],
                events_latitude=e[3],
                events_longitude=e[4],
                events_start=e[5] if type(e[5]) is datetime.datetime else None,
                events_finish=e[6] if type(e[6]) is datetime.datetime else None,
                events_type=e[7],
                fk_user_creator=str(e[8]),
                events_enable=e[9],
                events_delete=e[10],
                events_language=e[11],
                events_country=e[12],
                events_velocity=e[13],
                events_image=e[14],
                events_level=e[15],
                events_title_id=e[16],
                events_skins=e[17],
                events_fb_event_id=e[18],
                hashtags=e[19],
                events_cc=e[20],
                events_ip=e[21],
                events_fb_ids=str(e[22]),
                events_msg=e[23],
                events_img_str=e[24],
                events_sort=str(e[25]))
                ev.put()
            c.close()
            conn.close()
            return HttpResponse('')
        elif action=='3':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c.execute('SELECT users_id,users_name,users_name_id,users_lastname,users_firstname,users_email,users_password,users_fb_id,users_path_local_avatar,users_path_web_avatar,users_time_zone,fk_users_type,users_delete,users_birthday,users_sex,users_hashtags,users_date_joined,users_locale,users_middle_name,users_is_location_enable,users_is_nearby_enable FROM users')
            for e in c.fetchall():
                uss=UsersStore(
                    users_id=str(e[0]),
                    users_name=e[1],
                    users_name_id=str(e[2]),
                    users_lastname=e[3],
                    users_firstname=e[4],
                    users_email=e[5],
                    users_password=e[6],
                    users_fb_id=str(e[7]),
                    users_path_local_avatar=e[8],
                    users_path_web_avatar=e[9],
                    users_time_zone=e[10],
                    fk_users_type=str(e[11]),
                    users_delete=e[12],
                    users_birthday=e[13] if type(e[13]) is datetime.datetime else None,
                    users_sex=e[14],
                    users_hashtags=e[15],
                    users_date_joined=e[16] if type(e[16]) is datetime.datetime else None,
                    users_locale=e[17],
                    users_middle_name=e[18],
                    users_is_location_enable=e[19],
                    users_is_nearby_enable=e[20]
                )
                uss.put()
            c.close()
            conn.close()
            return HttpResponse('')
        elif action=='4':
            ppp=get_p(page)
            events=ndb.gql("SELECT * FROM Events WHERE events_delete = 0 LIMIT %s,%s"%(time.strftime("%Y-%m-%dT%H:%M:%S"),ppp[0],ppp[1]))
            o={}
            u={}
            r={}
            #r['count']=events.count()
            #if events.count()>0:
            #    r['n']='1'
            #else:
            #    r['n']='0'
            r['p']='0'
            d=[]
            c=0
            for e in events:
                c+=1
                uuu=ndb.gql("SELECT * FROM Users WHERE users_id=:1")
                uuu=uuu.bind(e.fk_user_creator).get()
                u['users_id']=uuu.users_id
                u['users_name_id']=uuu.users_name_id
                u['users_firstname']=uuu.users_firstname
                u['users_middle_name']=uuu.users_middle_name
                u['users_lastname']=uuu.users_lastname
                u['users_name']=uuu.users_name
                u['users_hashtags']=''
                u['users_path_web_avatar']=uuu.users_path_web_avatar
                o['events_id']=e.events_id
                o['events_title']=e.events_title
                o['events_description']=e.events_description
                o['events_latitude']=e.events_latitude
                o['events_longitude']=e.events_longitude
                o['events_start']=e.events_start.strftime('%Y-%m-%d %H:%M:%S') if e.events_start is not None else None,
                o['events_start']=o['events_start'][0]
                o['events_finish']=e.events_finish.strftime('%Y-%m-%d %H:%M:%S') if e.events_finish is not None else None,
                o['events_finish']=o['events_finish'][0]
                o['events_type']=e.events_type
                o['fk_users']=u
                o['events_language']=e.events_language
                o['events_country']=e.events_country
                o['events_velocity']=e.events_velocity
                o['events_image']=e.events_image
                o['events_title_id']=e.events_title_id
                o['events_skins']=e.events_skins
                o['hashtags']=e.hashtags
                o['events_img_str']=e.events_img_str
                o['events_sort']=e.events_sort
                d.append(o)
            r['r']=d
            r['count']=events.count()#c
            if c>0:
                r['n']='1'
            else:
                r['n']='0'
            return HttpResponse(json.dumps(r),content_type="application/json")
        elif action=='5':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            pp=get_p(page,500)
            c.execute('SELECT users_follows_events_id,users_follows_events_subscription_date,fk_users,fk_events FROM users_follows_events LIMIT %s,%s',(pp[0],pp[1]))
            for e in c.fetchall():
                ufe=UsersFollowsEventsStore(
                    users_follows_events_id=str(e[0]),
                    users_follows_events_subscription_date=e[1] if type(e[1]) is datetime.datetime else None,
                    fk_users=str(e[2]),
                    fk_events=str(e[3])
                )
                ufe.put()
            c.close()
            conn.close()
            return HttpResponse('')
        elif action=='6':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c.execute('SELECT users_writes_comments_id,users_writes_comments_content,fk_users,fk_events,users_writes_comments_delete FROM users_writes_comments')
            for e in c.fetchall():
                uwc=UsersWritesCommentsStore(
                    users_writes_comments_id=str(e[0]),
                    users_writes_comments_content=e[1],
                    fk_users=str(e[2]),
                    fk_events=str(e[3]),
                    users_writes_comments_delete=e[4]
                )
                uwc.put()
            c.close()
            conn.close()
            return HttpResponse('')
        elif action=='7':
            return HttpResponse(json.dumps({
                'e':EventsStore.query().count(),
                'u':UsersStore.query().count(),
                'ufe':UsersFollowsEventsStore.query().count(),
                'uwc':UsersWritesCommentsStore.query().count()
                }),content_type="application/json")
        elif action=='8':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c.execute('select events_id,events_title,events_title_id,fk_user_creator,events_finish from events where events_type=2 AND TIMESTAMPDIFF(SECOND,NOW(),events_finish) > 0 AND events_delete = 0')
            for e in c.fetchall():
                ev=EventsQueue(
                    events_id=str(e[0]),
                    events_title=e[1],
                    events_title_id=e[2],
                    fk_user_creator=str(e[3]),
                    events_finish=e[4],
                    events_alert_minutes=5
                )
                ev.put()
            c.close()
            conn.close()
        else:
            return HttpResponse('')
    if request.method=='POST':
        return HttpResponse('')
    return HttpResponse('')
def get_events_21(request):
    if request.method=='POST':
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        str_token=request.session.get('sessiontoken','')
        form=Event(request.POST)
        if form.is_valid():
            types=['me','user','new','hot','ending','hashtag','following','draft','facebook','finished','nearby']
            p=form.cleaned_data['page']
            t=form.cleaned_data['type']
            id=form.cleaned_data['id']
            img_size=form.cleaned_data['img_size']
            search=slugify_sp(form.cleaned_data['search'])
            device=form.cleaned_data['device']
            ##LIMPIAR search (ESCAPAR)
            if (t=="me" or t=="following" or t=='draft' or t=='facebook') and str_token=='' and token=='' and valid_token(str_token) is None and valid_token(token) is None:
                return HttpResponse(json.dumps({}),content_type="application/json")
            u_id=None
            res=[]
            d={}
            u_id=0
            #p=int(p)
            id=int(id)
            n_r=0
            country=''
            if img_size is not None:
                if img_size>1000:
                    img_size=1000
            else:
                img_size=500
            if p>0 and id>=0 and (t in types):
                curs=Cursor(urlsafe=str(p))
                events,next_curs,more=EventsStore.query().fetch_page(20,start_cursor=curs)
                for e in events:
                    dt={}
                    dt['events_id']=e.events_id
                    res.append(dt)
                d['r']=res
                if more and next_curs:
                    d['n']='1'
                else:
                    d['n']='0'
                return HttpResponse(json.dumps(d),content_type="application/json")
            return HttpResponse(json.dumps({}),content_type="application/json",status=400)
        return HttpResponse(json.dumps(form.errors),content_type="application/json",status=400)
                    
        
def event_details_str_api_21(request,idx=None):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        u_id=None
        e=ndb.gql("SELECT * FROM Events WHERE events_title_id=:1 AND events_delete=0",idx).get()
        if e is None:
            return HttpResponse(json.dumps({}),content_type="application/json",status=404)
        else:
            if str_token.strip()!='':
                u_id=valid_token(str_token)
            if token.strip()!='':
                u_id=valid_token(token)
            if (str_token.strip()=='' and token.strip()=='') or (u_id is None):
                o={}
                u={}
                uuu=ndb.gql("SELECT * FROM Users WHERE users_id=:1",e.fk_user_creator).get()
                ufe=ndb.gql("SELECT * FROM UsersFollowsEvents WHERE fk_events=:1",e.events_id)
                uwc=ndb.gql("SELECT * FROM UsersWritesComments WHERE fk_events=:1",e.events_id)
                o['events_likes']=len(ufe.fetch(keys_only=True))
                o['events_comments']=len(uwc.fetch(keys_only=True))
                u['users_id']=uuu.users_id
                u['users_name_id']=uuu.users_name_id
                u['users_firstname']=uuu.users_firstname
                u['users_middle_name']=uuu.users_middle_name
                u['users_lastname']=uuu.users_lastname
                u['users_name']=uuu.users_name
                u['users_hashtags']=''
                u['users_path_web_avatar']=uuu.users_path_web_avatar
                o['events_id']=e.events_id
                o['events_title']=e.events_title
                o['events_description']=e.events_description
                o['events_latitude']=e.events_latitude
                o['events_longitude']=e.events_longitude
                o['events_start']=e.events_start.strftime('%Y-%m-%d %H:%M:%S') if e.events_start is not None else None,
                o['events_start']=o['events_start'][0]
                o['events_finish']=e.events_finish.strftime('%Y-%m-%d %H:%M:%S') if e.events_finish is not None else None,
                o['events_finish']=o['events_finish'][0]
                o['events_type']=e.events_type
                o['fk_users']=u
                o['events_language']=e.events_language
                o['events_country']=e.events_country
                o['events_velocity']=e.events_velocity
                o['events_image']=e.events_image
                o['events_title_id']=e.events_title_id
                o['events_skins']=e.events_skins
                o['hashtags']=e.hashtags
                o['events_img_str']=e.events_img_str
                o['events_sort']=e.events_sort
                o['events_seconds']=int((datetime.datetime.now()-e.events_start).total_seconds()) if e.events_type=='timer' else int((e.events_finish-datetime.datetime.now()).total_seconds())
                return HttpResponse(json.dumps(o),content_type="application/json")
            else:
                o={}
                u={}
                uuu=ndb.gql("SELECT * FROM Users WHERE users_id=:1",e.fk_user_creator).get()
                ufe=UsersFollowsEventsStore.query(UsersFollowsEventsStore.fk_events==e.events_id)
                uufe=ufe.filter(UsersFollowsEventsStore.fk_users==str(u_id[0]))
                uwc=UsersWritesCommentsStore.query(UsersWritesCommentsStore.fk_events==e.events_id)
                uuwc=uwc.filter(UsersWritesCommentsStore.fk_users==str(idx))
                if uufe.count()<=0:
                    o['is_user_follow']=0
                else:
                    o['is_user_follow']=1
                if uuwc.count()<=0:
                    o['is_user_comment']=0
                else:
                    o['is_user_comment']=1
                o['events_likes']=len(ufe.fetch(keys_only=True))
                o['events_comments']=len(uwc.fetch(keys_only=True))
                u['users_id']=uuu.users_id
                u['users_name_id']=uuu.users_name_id
                u['users_firstname']=uuu.users_firstname
                u['users_middle_name']=uuu.users_middle_name
                u['users_lastname']=uuu.users_lastname
                u['users_name']=uuu.users_name
                u['users_hashtags']=''
                u['users_path_web_avatar']=uuu.users_path_web_avatar
                o['events_id']=e.events_id
                o['events_title']=e.events_title
                o['events_description']=e.events_description
                o['events_latitude']=e.events_latitude
                o['events_longitude']=e.events_longitude
                o['events_start']=e.events_start.strftime('%Y-%m-%d %H:%M:%S') if e.events_start is not None else None,
                o['events_start']=o['events_start'][0]
                o['events_finish']=e.events_finish.strftime('%Y-%m-%d %H:%M:%S') if e.events_finish is not None else None,
                o['events_finish']=o['events_finish'][0]
                o['events_type']=e.events_type
                o['fk_users']=u
                o['events_language']=e.events_language
                o['events_country']=e.events_country
                o['events_velocity']=e.events_velocity
                o['events_image']=e.events_image
                o['events_title_id']=e.events_title_id
                o['events_skins']=e.events_skins
                o['hashtags']=e.hashtags
                o['events_img_str']=e.events_img_str
                o['events_sort']=e.events_sort
                o['events_seconds']=int((datetime.datetime.now()-e.events_start).total_seconds()) if e.events_type=='timer' else int((e.events_finish-datetime.datetime.now()).total_seconds())
                return HttpResponse(json.dumps(o),content_type="application/json")
def create_event_21(request):
    if request.method=='POST':
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        str_token=request.session.get('sessiontoken','')
        form=Event(request.POST)
        if form.is_valid():
            return HttpResponse('A')
        return HttpResponse('B')

def sec_to_time(sec):
    days = sec / 86400
    sec -= 86400*days

    hrs = sec / 3600
    sec -= 3600*hrs

    mins = sec / 60
    sec -= 60*mins
    return [days,hrs,mins,sec]

def render_image(request,id):
    if request.method=='GET':
        CLOUDSQL_INSTANCE='festive-ally-585:oclock'
        DATABASE_NAME='oclock'
        USER_NAME='root'
        conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
        c=conn.cursor()
        c_n=conn.cursor()
        c.execute('SELECT events_image_stamp,events_id from events WHERE events_id=%s',(id,))
        ev=c.fetchone()
        if ev is not None:
            """arrt=sec_to_time(ev[1])
            time='%dH %dM %dS'%(arrt[1],arrt[2],arrt[3])
            file=cStringIO.StringIO(urllib2.urlopen(ev[0]).read())"""
            #img=Image.open(img)
            #img=urllib2.urlopen('https://storage.googleapis.com/oclock-static/c13c9b8a251b020f222f2a1b7acca15817c461aa.jpg')
            #file=remote_image(img)
            """if ev[2]=='love':
                timestamp(file,arrt[0],time,response,1)
            else:
                if arrt[0]>0:
                    time='%dD %dH %dM'%(arrt[0],arrt[1],arrt[2])
                timestamp(file,arrt[0],time,response,0)"""
            response=HttpResponse(mimetype="image/png")
            if ev[0] is not None and ev[0]!='':
                remote_to_img(ev[0],response)
            else:
                #c_n.execute('UPDATE events SET events_image_stamp=%s WHERE events_id=%s',('https://storage.googleapis.com/oclock-images/default.jpg',ev[1]))
                #conn.commit()
                remote_to_img('https://storage.googleapis.com/oclock-images/default_normal.png',response)
            c.close()
            c_n.close()
            conn.close()
            return response
        else:
            c.close()
            c_n.close()
            conn.close()
            return HttpResponse('')
    return HttpResponse('')
def get_friends(request):
    if request.method=='POST':
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ","").strip()
        d={}
        str_token=request.session.get('sessiontoken','')
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if token.strip()!='':
            u_id=valid_token(token)
        if (str_token.strip()!='' and u_id is not None):
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')            
            c=conn.cursor()
            c.execute("SELECT social_networks_token FROM social_networks WHERE fk_users=%s",(request.session.get('users_id',0),))
            fb_tk=c.fetchone()
            friends=json.load(urllib.urlopen("https://graph.facebook.com/me/friends?"+urllib.urlencode(dict(access_token=fb_tk[0]))))
            template_values={"fb_fr":friends}
            c.close()
            conn.commit()
            conn.close()
            return HttpResponse(json.dumps(template_values),content_type="application/json")
        if (token!='' and u_id is not None):
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            c.execute("SELECT user_id FROM oauth2_accesstoken WHERE token=%s",(token,))
            u_id=c.fetchone()
            c.execute("SELECT social_networks_token FROM social_networks WHERE fk_users=%s",(u_id,))
            fb_tk=c.fetchone()
            friends=json.load(urllib.urlopen("https://graph.facebook.com/me/friends?"+urllib.urlencode(dict(access_token=fb_tk[0]))))
            template_values={"fb_fr":friends}
            c.close()
            conn.commit()
            conn.close()
            return HttpResponse(json.dumps(template_values),content_type="application/json")
        return HttpResponse(json.dumps({'message':'error token'}),status=401)
    return HttpResponse(json.dumps({'message':'error method http'}),status=401)
def check_event(request):
    return HttpResponse(json.dumps({'status':'on'}),content_type="application/json")
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import StringIO
def min_all_images(request):
    p=int(request.REQUEST.get('page'))
    conn=mysqlconn()
    c=conn.cursor()
    pp=get_p(p,50)
    c.execute('SELECT events_id,events_image FROM events where events_image not like %s AND events_id=%s',('%http:%',p))
    val=str(c.rowcount)
    for ev in c.fetchall():
        try:
            img=cStringIO.StringIO(urllib2.urlopen(ev[1]).read())
            
            img=thumbnail_image(img)
        
            thumb_io=StringIO.StringIO()
            omg=InMemoryUploadedFile(thumb_io,None,'foo.jpg','image/jpeg',thumb_io.len,None)
            img.save(omg,quality=80,optimize=True)
            
            rem=remote_image2(omg)
            c.execute('UPDATE events SET events_image=%s WHERE events_id=%s',(rem,ev[0]))
            conn.commit()
            files.delete("/gs%s"%ev[1][30:])
            del omg
            del img
        except:
            continue
    #https://storage.googleapis.com/oclock-static/7b8de27e5778228cc5eb68cb912138a06a418fc5.jpg
    c.close()
    conn.close()
    return HttpResponse("%s - %s"%(val,p))
import traceback
def stamp_all_images(request):
    p=int(request.REQUEST.get('page'))
    cant=int(request.REQUEST.get('cant'))
    conn=mysqlconn()
    c=conn.cursor()
    cn=conn.cursor()
    pp=get_p(p,cant)
    c.execute('SELECT events_id,events_image,events_type_special FROM events where events_delete=0 and events_id=%s ',(p,))
    val=str(c.rowcount)
    err=0
    for ev in c.fetchall():
        try:
            if ev[1] is not None and ev[1]!='':
                img=cStringIO.StringIO(urllib2.urlopen(ev[1]).read())
                img=create_img(img)
                #img=thumbnail_image(img)
                if ev[2]=='love':
                    img=images_stamp(img,1)
                else:
                    img=images_stamp(img,0)
                thumb_io=StringIO.StringIO()
                omg=InMemoryUploadedFile(thumb_io,None,'foo.jpg','image/jpeg',thumb_io.len,None)
                try:
                    img.save(omg,quality=60,optimize=True,progressive=True)
                except IOError:
                    img.save(omg,quality=80)
                
                rem=remote_image2(omg)
                cn.execute('UPDATE events SET events_image_stamp=%s WHERE events_id=%s',(rem,ev[0]))
                conn.commit()
                #files.delete("/gs%s"%ev[1][30:])
                del omg
                del img
            else:
                cn.execute('UPDATE events SET events_image_stamp=%s WHERE events_id=%s',('https://storage.googleapis.com/oclock-images/default_normal.png',ev[0]))
                conn.commit()
        except:
            err+=1
            cn.execute('UPDATE events SET events_image_stamp=%s WHERE events_id=%s',('https://storage.googleapis.com/oclock-images/default_normal.png',ev[0]))
            conn.commit()
            traceback.print_exc()
            continue
    #https://storage.googleapis.com/oclock-static/7b8de27e5778228cc5eb68cb912138a06a418fc5.jpg
    c.close()
    cn.close()
    conn.close()
    return HttpResponse("%s - %s : %s"%(val,p,err))

def like_event(request,id):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ",'').strip()
        redirect=request.REQUEST.get('r',None)
        if str_token=='' and token=='':
            return HttpResponse(json.dumps({}),content_type="application/json")
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
            #u_id=int(request.session.get('users_id',0))
            n_follow=0
            id=int(id)
            r=''
            c.execute('SELECT COUNT(*) as count FROM events WHERE events_id=%s',(id))
            n_ev=int(c.fetchone()[0])
            if n_ev>0:
                c.execute('SELECT COUNT(*) as count FROM users_follows_events WHERE fk_users=%s AND fk_events=%s',(u_id,id))
                n_fo=int(c.fetchone()[0])
                if n_fo>0:
                    c.execute('DELETE FROM users_follows_events WHERE fk_users=%s AND fk_events=%s;',(u_id,id))
                    c.execute('SELECT COUNT(*) as count FROM users_follows_events WHERE fk_events=%s',(id,))
                    n_follow=c.fetchone()[0]
                    r='n_f'
                else:
                    c.execute('DELETE FROM users_follows_events WHERE fk_users=%s AND fk_events=%s',(u_id,id))
                    c.execute('INSERT INTO users_follows_events(fk_users,fk_events,users_follows_events_subscription_date) VALUES(%s,%s,%s)',(u_id,id,datetime.datetime.now()))
                    c.execute('SELECT COUNT(*) as count FROM users_follows_events WHERE fk_events=%s',(id,))
                    n_follow=c.fetchone()[0]
                    r='f'
                    notifAll(id,u_id[0],2)
                c.close()
                conn.commit()
                conn.close()
                if redirect is not None and redirect.strip()!='':
                    return HttpResponseRedirect("%s"%redirect)
                else:
                    return HttpResponse(json.dumps({'r':r,'n':n_follow}),content_type="application/json")
            return HttpResponse('e')
        return HttpResponse('e')
    return HttpResponse('e',status=401)
def events_read(request):
    if request.method=='GET':
        str_token=request.session.get('sessiontoken','')
        token=str(request.META.get('HTTP_AUTHORIZATION',''))
        token=token.replace("Bearer ",'').strip()
        if str_token=='' and token=='':
            return HttpResponse(json.dumps({}),content_type="application/json",status=400)
        u_id=None
        if str_token.strip()!='':
            u_id=valid_token(str_token)
        if token.strip()!='':
            u_id=valid_token(token)
        if u_id is not None:
            conn=mysqlconn()
            c=conn.cursor()
            c.execute('UPDATE activities SET activities_read=1 WHERE fk_user=%s AND activities_read=0',(u_id,))
            conn.commit()
            c.close()
            conn.close()
            return HttpResponse(json.dumps({'status':'read'}),content_type="application/json")
        return HttpResponse(json.dumps({}),content_type="application/json",status=400)
    return HttpResponse(json.dumps({}),content_type="application/json",status=400)