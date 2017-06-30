'''
Created on 19-09-2014
@author: carriagadad
'''
from django.http import HttpResponse
import urllib2
import json
import urllib
import hashlib
from google.appengine.api import rdbms
import time
from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import images
from datetime import datetime,timedelta
from dateutil import tz
import unicodedata,re
from oclock.apps.mailing.services import Mandrill_Services
from django.template import RequestContext,loader,Context
import webapp2
from google.appengine.api import urlfetch
from oclock.apps.media.images import remote_image
from oclock.apps.db.datastore import EventsQueue
from google.appengine.ext import ndb
#import logging
"""def _get_connection():
    CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
    DATABASE_NAME = 'oclock'
    USER_NAME = 'root'
    return rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')"""
def get_p(p,c=2):
    r=[]
    r_by_p=c
    l_l=(p-1)*r_by_p
    r.append(l_l)
    r.append(r_by_p)
    return r
def slugify(str):
    slug=unicodedata.normalize("NFKD",unicode(str)).encode("ascii", "ignore")
    slug=re.sub(r"[^\w]+"," ",slug)
    slug="-".join(slug.lower().strip().split())
    return slug
class CronEventsQueue(webapp2.RequestHandler):
    def get(self):
        if self.request.remote_addr=='0.1.0.1':
            nt=datetime.now()
            ms=Mandrill_Services()
            eq=EventsQueue.query(ndb.AND(
                EventsQueue.events_finish>=nt,
                EventsQueue.events_finish<nt+timedelta(minutes=8)
            ))
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME = 'root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            c=conn.cursor()
            for e in eq:
                c.execute('SELECT users_name,users_email FROM users WHERE users_id=%s',(e.fk_user_creator))
                user=c.fetchone()
                c.execute('SELECT u.users_name as users_name_sub,u.users_email as users_email_sub FROM users_follows_events ufe LEFT JOIN users u ON u.users_id=ufe.fk_users WHERE fk_events=%s;',(e.events_id,))
                for (users_name_sub,users_email_sub) in c:
                    if user[1]!=users_email_sub:
                        template_values={'events_title':e.events_title,'events_title_id':e.events_title_id}
                        t=loader.get_template('oclock/mail/clock_finished_sub_after_beta.html')
                        rc=RequestContext(self.request,template_values)
                        #c=Context(template_values)
                        html=t.render(rc)
                        ms.send_mail(users_email_sub,'It\'s time for '+e.events_title,html)
                template_values={'events_title':e.events_title,'events_title_id':e.events_title_id}
                t=loader.get_template('oclock/mail/clock_finished_after_beta.html')
                rc=RequestContext(self.request,template_values)
                html=t.render(rc)
                ms.send_mail(user[1],'It\'s time for '+e.events_title,html)
                if e is not None:
                    e.key.delete()
            c.close()
            conn.close()
            self.response.write('')
        self.response.write('')
            
class CronListMedium(webapp2.RequestHandler):
    def get(self):
        if self.request.remote_addr=='0.1.0.1':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME = 'root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            cursor=conn.cursor()
            cursor_in=conn.cursor()
            cursor.execute('INSERT INTO events_high (SELECT * from events_medium where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 30);')
            cursor.execute('DELETE FROM events_medium where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 30')
            cursor.execute('INSERT INTO test VALUES (\''+self.request.remote_addr+'\');')
            cursor.close()
            cursor_in.close()
            conn.commit()
            conn.close()
            self.response.write('')
        self.response.write('')
def cron_tasks(request):
    if request.method=='GET' and request.META['REMOTE_ADDR']=='0.1.0.1':
        CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
        DATABASE_NAME = 'oclock'
        USER_NAME = 'root'
        conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
        cursor=conn.cursor()
        cursor_in=conn.cursor()
        
        cursor.execute('INSERT INTO events_high (SELECT * from events_medium where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 30);')
        cursor.execute('DELETE FROM events_medium where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 30')
        
        cursor.execute('insert into test values (\''+request.META['REMOTE_ADDR']+'\');')
        
        #cursor.execute('TRUNCATE TABLE events_hot')
        #cursor.execute('DELETE FROM events_hot WHERE events_id>0')
        #cursor.execute('INSERT INTO events_hot (SELECT e.* from events e LEFT JOIN users_follows_events ufe ON ufe.fk_events=e.events_id GROUP BY e.events_id ORDER BY count(*) DESC)')
            
            #for interest in interests.get('data',[]):
            #    pass

        #opener = urllib2.build_opener()
        #opener.addheaders = [('', '')]
        #try: 
        #    res=opener.open(events_json['paging']['next'],None,60)
        #    j = res.read()
        #    events_json=json.loads(j)
        #    if len(events_json['data'])<=0:
        #        break
        #except urllib2.HTTPError, err:
        #    break
                    
        cursor.close()
        cursor_in.close()
        conn.commit()
        conn.close()
        return HttpResponse('')
    return HttpResponse('')

import logging
import sys
import traceback
class CronListHigh(webapp2.RequestHandler):
    def get(self):
        if self.request.remote_addr=='0.1.0.1':
            CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
            DATABASE_NAME = 'oclock'
            USER_NAME = 'root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            cursor=conn.cursor()
            cursor_in=conn.cursor()
            try:
                """cursor.execute('SELECT u.users_name,u.users_email,e.events_id,e.events_title,e.events_title_id from events_high e left join users u on u.users_id = e.fk_user_creator where e.events_type=2 AND TIMESTAMPDIFF(minute,NOW(),e.events_finish) <= 10')
                ms=Mandrill_Services()
                for (users_name,users_email,events_id,events_title,events_title_id) in cursor:
                    cursor_in.execute('SELECT u.users_name as users_name_sub,u.users_email as users_email_sub FROM users_follows_events ufe LEFT JOIN users u ON u.users_id=ufe.fk_users WHERE fk_events=%s;',(events_id,))
                    for (users_name_sub,users_email_sub) in cursor_in:
                        if users_email!=users_email_sub:
                            template_values={'events_title':events_title,'events_title_id':events_title_id}
                            t=loader.get_template('oclock/mail/clock_finished_sub_after_beta.html')
                            c=RequestContext(self.request,template_values)
                            #c=Context(template_values)
                            html=t.render(c)
                            ms.send_mail(users_email_sub,'It\'s time for '+events_title,html)
                    template_values={'events_title':events_title,'events_title_id':events_title_id}
                    t=loader.get_template('oclock/mail/clock_finished_after_beta.html')
                    c=RequestContext(self.request,template_values)
                    html=t.render(c)
                    ms.send_mail(users_email,'It\'s time for '+events_title,html)
                    cursor.execute('DELETE FROM events_high where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 10')
                conn.commit()"""
                
                cursor.execute('SELECT seq_value FROM _sequence_cron WHERE seq_name="cron_facebook"')
                fq=cursor.fetchone()
                if fq is not None:
                    qw=get_p(fq[0])
                    cursor.execute('SELECT fk_users,social_networks_token FROM social_networks ORDER BY fk_users LIMIT %s,%s',(qw[0],qw[1]))
                    if cursor.rowcount>0:
                        cursor_in.execute('UPDATE _sequence_cron SET seq_value=%s WHERE seq_name="cron_facebook"',(int(fq[0])+1,))
                    else:
                        cursor_in.execute('UPDATE _sequence_cron SET seq_value=%s WHERE seq_name="cron_facebook"',(1,))
                        
                    for (fk_users,social_networks_token) in cursor:
                        profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+urllib.urlencode(dict(access_token=social_networks_token))))
                        #{"username": "carriagadad", "first_name": "Carlos", "last_name": "Arriagada Devia", "middle_name": "Andr\u00e9s", "name": "Carlos Andr\u00e9s Arriagada Devia", "locale": "en_US", "gender": "male", "verified": true, "email": "hackreader@hotmail.com", "link": "https://www.facebook.com/carriagadad", "timezone": -4, "updated_time": "2014-07-17T04:25:00+0000", "id": "1088104827"}"""
                        friends=json.load(urllib.urlopen("https://graph.facebook.com/me/friends?"+urllib.urlencode(dict(access_token=social_networks_token))))
                        #data": [{"name": "Wanting Qu", "id": "502500281"}, {"name": "S\u00edlvia Soares Boyer", "id": "509598243"}, {"name": "Luz Lopez", "id": "514874152"}"""
                        #interests=json.load(urllib.urlopen("https://graph.facebook.com/me/interests?"+urllib.urlencode(dict(access_token=social_networks_token))))
                        likes=json.load(urllib.urlopen("https://graph.facebook.com/me/likes?"+urllib.urlencode(dict(access_token=social_networks_token))))
                        #data":[{"category": "Musician/band", "created_time": "2014-04-27T04:18:24+0000", "name": "Official Assemblage 23", "id": "138651156153800"}, {"category": "Musician/band", "created_time": "2014-04-27T04:17:52+0000", "name": "Coldplay", "id": "15253175252"}, {"category": "Radio station", "created_time": "2014-04-17T22:42:03+0000", "name": "MusicaAnimes", "id": "279689688780026"}, {"category": "Aerospace/defense", "created_time": "2014-04-14T17:50:51+0000", "name": "NASA - National Aeronautics and Space Administration", "id": "54971236771"},]"""
                        events=json.load(urllib.urlopen("https://graph.facebook.com/me/events?"+urllib.urlencode(dict(access_token=social_networks_token))))
                        #data": [{"name": "2da junta Hunter X Chile", "rsvp_status": "attending", "start_time": "2014-08-09T14:30:00-0400", "location": "Serrano 74, Santiago", "timezone": "America/Santiago", "id": "602653779831802", "end_time": "2014-08-09T19:30:00-0400"}, {"name": "LOCOMOTION (GRATIS): HUNTER X HUNTER THE LAST MISSION", "rsvp_status": "attending", "start_time": "2014-08-02T17:00:00-0500", "location": "AUDITORIO DE LA UPT ( centro)", "timezone": "America/Lima", "id": "1462547874012560", "end_time": "2014-08-02T20:00:00-0500"}]}"""
                        #access_token_json=json.load(urllib.urlopen("https://graph.facebook.com/debug_token?"+urllib.urlencode(dict(input_token=serializer.object.social_networks_token))+"&"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
                        
                        ttp=profile.get("id",0)
                        if ttp==0:
                            cursor_in.execute('UPDATE social_networks SET social_networks_enable=0 WHERE fk_users=%s',(fk_users,))
                            conn.commit()
                            continue
                        
                        img=urllib2.urlopen(urllib2.Request('https://graph.facebook.com/'+profile["id"]+'/picture?type=large'),timeout=120)
                        cursor_in.execute('SELECT users_path_local_avatar from users where users_path_local_avatar=%s and users_id=%s',(img.geturl(),fk_users))
                        upla=cursor_in.fetchone()
                        if upla==None:
                            file_name_hash=remote_image(img)
                            cursor_in.execute('UPDATE users SET users_path_web_avatar=%s,users_path_local_avatar=%s WHERE users_id=%s',(file_name_hash,img.geturl(),fk_users))
                            
                        for hash in likes.get('data',[]):
                            if hash['name'].strip()!="":
                                hash_str=hash['name'].strip()
                                hash_val=slugify(hash['name'].replace('?', ' ').strip())
                                
                                cursor_in.execute('select hashtags_id from hashtags where hashtags_value=%s',(hash_val,))
                                h=cursor_in.fetchone()
                                
                                if h==None:
                                    cursor_in.execute('INSERT INTO hashtags(hashtags_value,hashtags_value_str) VALUES(%s,%s)',(hash_val,hash_str))
                                    cursor_in.execute('SELECT hashtags_id FROM hashtags where hashtags_value=%s',(hash_val,))
                                    h=cursor_in.fetchone()                
                                #cursor_in.execute("""select if (exists(select users_has_hashtags_id from users_has_hashtags where fk_users=%s and fk_hashtags=%s),(select hashtags_id from users_has_hashtags where fk_users=%s and fk_hashtags=%s),0)""",(fk_users,h,fk_users,h))
                                cursor_in.execute('SELECT users_has_hashtags_id FROM users_has_hashtags WHERE fk_users=%s and fk_hashtags=%s',(fk_users,h))
                                uhh=cursor_in.fetchone()
                                if uhh==None:
                                    cursor_in.execute('INSERT INTO users_has_hashtags(fk_users,fk_hashtags) VALUES(%s,%s)',(fk_users,h))
                        
                        for event in events.get('data',[]):
                            #logging.debug(event['id'])
                            #pendiente obtener la zona horaria de timezone
                            if event.get('timezone',False)!=False:
                                try:
                                    local=event['start_time']
                                    #z=Zone.objects.get(zone_name__icontains=event['timezone'])
                                    #datetime.datetime.now() ValueError: invalid literal for int() with base 10: '2014-08-06 23:02:52.163880'
                                    #tz=Timezone.objects.filter(zone_id=z.zone_id,time_start__lte=datetime.now()).order_by('-time_start')[:1]
                                    #start_t=event['start_time']+timedelta(seconds=tz.gmt_offset) 
                                    #gmt_offset seconds
                                    from_zone=tz.gettz(event.get('timezone','UTC'))
                                    to_zone=tz.gettz('UTC')
                                    if len(event['start_time'])<=10: #0000-00-00
                                        local=datetime.strptime(event['start_time'],'%Y-%m-%d')
                                    if len(event['start_time'])==19: #0000-00-00T00:00:00
                                        local=datetime.strptime(event['start_time'],'%Y-%m-%dT%H:%M:%S')
                                    if len(event['start_time'])>19: #0000-00-00T00:00:00
                                        local=datetime.strptime(event['start_time'][:-5],'%Y-%m-%dT%H:%M:%S')
                                    local=local.replace(tzinfo=from_zone)
                                    utc=local.astimezone(to_zone)
                                    start_t=utc.strftime("%Y-%m-%d %H:%M:%S") #event['start_time']
                                except ValueError:
                                    continue
                            else:
                                try:
                                    if len(event['start_time'])<=19: #0000-00-00 or 2012-04-07T11:00:00
                                        if len(event['start_time'])<=10:
                                            start_t=event['start_time']+' 00:00:00'
                                        else:
                                            start_t=event['start_time']
                                    else:
                                        if event['start_time'][-5:-4]=='-':
                                            start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")-timedelta(hours=int(event['start_time'][-4:-2]))
                                        else:
                                            start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")+timedelta(hours=int(event['start_time'][-4:-2]))
                                except ValueError:
                                    continue
                            opener = urllib2.build_opener()
                            opener.addheaders = [('', '')]
                            event_json={}
                            try: 
                                res=opener.open('https://graph.facebook.com/'+event['id']+'?'+urllib.urlencode(dict(access_token=social_networks_token)),None,60)
                                j = res.read()
                                event_json=json.loads(j)
                                #event_json['privacy'] OPEN-SECRET-FRIENDS
                                #event_json['owner']['id']
                            except urllib2.HTTPError,err:
                                pass
                            if event_json.get('privacy','')=='OPEN':
                                logging.debug(event['id'])
                                #https://graph.facebook.com/1462547874012560/picture?type=large
                                #events=Events.objects.get(events_fb_event_id=event['id'])
                                cursor_in.execute('SELECT events_id FROM events WHERE events_fb_event_id=%s',(event['id'],))
                                ev_id=cursor_in.fetchone()
                                if ev_id==None:
                                    try:
                                        ccc=None
                                        opener = urllib2.build_opener()
                                        opener.addheaders = [('', '')]
                                        file_name_hash=None
                                        try: 
                                            res=opener.open('https://graph.facebook.com/fql?'+urllib.urlencode(dict(q='SELECT pic_cover,venue FROM event WHERE eid='))+event['id']+'&'+urllib.urlencode(dict(access_token=social_networks_token)),None,60)
                                            j=res.read()
                                            event_images=json.loads(j)
                                            if event_images['data'][0]['pic_cover'] is not None:
                                                img=urllib2.urlopen(event_images['data'][0]['pic_cover']['source'])
                                                file_name_hash=remote_image(img)
                                            country=event_images['data'][0]['venue']
                                            if country and len(country)>0:
                                                cursor_in.execute('SELECT country_code FROM country WHERE country_name LIKE %s',('%'+country['country']+'%',))
                                                ccc=cursor_in.fetchone()
                                        except urllib2.HTTPError, err:
                                            pass
                                        if file_name_hash is not None:
                                            file_name_hash=file_name_hash
                                        events_title_id=event['name']
                                        e_title=event['name'].replace('-', ' ').strip()
                                        e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                                        e_title=slugify(e_title)
                                        if len(e_title.strip())==0:
                                            e_title='oclock';
                                        #verificar si existe
                                        #n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                                        cursor_in.execute("SELECT COUNT(*) FROM events WHERE events_title_id LIKE '%"+e_title+"'")
                                        n_title=cursor_in.fetchone()
                                        if n_title[0] > 0:
                                            events_title_id=e_title+'-'+str(n_title[0])
                                        else:
                                            events_title_id=e_title
                                    
                                        if profile["id"]==event_json['owner']['id']:
                                            creator=fk_users
                                            cursor_in.execute('INSERT INTO events(events_title,events_finish,events_skins,events_type,events_velocity,events_level,events_delete,events_enable,fk_user_creator,events_title_id,events_image,events_fb_event_id,events_cc) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(event['name'],start_t,'skin1',2,1000,1,0,1,fk_users,events_title_id,file_name_hash,event['id'],ccc))
                                        else:
                                            creator=1818
                                            cursor_in.execute('INSERT INTO events(events_title,events_finish,events_skins,events_type,events_velocity,events_level,events_delete,events_enable,fk_user_creator,events_title_id,events_image,events_fb_event_id,events_cc) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(event['name'],start_t,'skin1',2,1000,1,0,1,1818,events_title_id,file_name_hash,event['id'],ccc))
                                        #cursor_in.execute("SELECT events_id FROM events WHERE events_title_id LIKE '%"+events_title_id+"'")
                                        #e_id=conn.insert_id()#cursor_in.fetchone()[0]
                                        e_id=cursor_in.lastrowid
                                        
                                        ev=EventsQueue(
                                            events_id=str(e_id),
                                            events_title=event['name'][:500],
                                            events_title_id=events_title_id,
                                            fk_user_creator=str(creator),
                                            events_finish=datetime.strptime(start_t,"%Y-%m-%d %H:%M:%S") if type(start_t) in [str,unicode] else start_t,
                                            events_alert_minutes=5
                                        )
                                        ev.put()
                                        
                                        cursor_in.execute('INSERT INTO events_from_facebook(fk_users,fk_events,events_from_facebook_date) VALUES(%s,%s,%s)',(fk_users,e_id,datetime.now()))
                                        cursor_in.execute('INSERT INTO users_follows_events(fk_users,fk_events,users_follows_events_subscription_date) VALUES(%s,%s,%s)',(113,e_id,datetime.now()))
                                        
                                        cursor_in.execute('SELECT fk_users,fk_events FROM users_follows_events WHERE fk_users=%s AND fk_events=%s',(fk_users,e_id))
                                        ufe=cursor_in.fetchone()
                                        if ufe==None:                        
                                            cursor_in.execute('INSERT INTO users_follows_events(fk_users,fk_events,users_follows_events_subscription_date) VALUES(%s,%s,%s)',(fk_users,e_id,datetime.now()))
                                        conn.commit()
                                    except KeyError:
                                        pass
                                else:
                                    try:
                                        #ev_id=str(ev_id)
                                        events_finish=start_t
                                        events_title=event['name']
                                        #events.events_image=file_name_hash
                                        if profile["id"]==event_json['owner']['id'] and fk_users is not None:
                                            cursor_in.execute('UPDATE events SET events_finish=%s,events_title=%s,fk_user_creator=%s WHERE events_id=%s',(events_finish,events_title,fk_users,ev_id))
                                        cursor_in.execute('UPDATE events SET events_finish=%s,events_title=%s WHERE events_id=%s',(events_finish,events_title,ev_id))
                                        cursor_in.execute('SELECT COUNT(*) FROM events_from_facebook WHERE fk_users=%s AND fk_events=%s',(fk_users,ev_id))
                                        nnz=cursor_in.fetchone()[0]
                                        if nnz<=0:
                                            cursor_in.execute('INSERT INTO events_from_facebook(fk_users,fk_events) VALUES(%s,%s)',(fk_users,ev_id))
                                        cursor_in.execute('SELECT fk_users,fk_events FROM users_follows_events WHERE fk_users=%s AND fk_events=%s',(fk_users,ev_id))
                                        ufe=cursor_in.fetchone()
                                        if ufe==None:                        
                                            cursor_in.execute('INSERT INTO users_follows_events(fk_users,fk_events,users_follows_events_subscription_date) VALUES(%s,%s,%s)',(fk_users,ev_id,datetime.now()))
                                    except KeyError:
                                        pass
                        #cursor_in.execute('DELETE FROM users_has_friends WHERE fk_user_from=%s',(fk_users,))
                        for friend in friends.get('data',[]):
                            cursor_in.execute('SELECT users_id FROM users WHERE users_fb_id=%s',(friend['id'],))
                            uuf=cursor_in.fetchone()
                            if uuf is not None:
                                cursor_in.execute('SELECT COUNT(*) FROM users_has_friends WHERE (fk_user_from=%s AND fk_user_to=%s) OR (fk_user_from=%s AND fk_user_to=%s) ',(fk_users,uuf,uuf,fk_users))
                                ff=cursor_in.fetchone()
                                if ff[0]==0:
                                    cursor_in.execute('INSERT INTO users_has_friends(fk_user_from,fk_user_to) VALUES(%s,%s)',(fk_users,uuf))
                        time.sleep(5)
                
                cursor.close()
                cursor_in.close()
                conn.commit()
                conn.close()
            except NameError:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logging.debug(''.join('!! ' + line for line in lines))
                cursor.close()
                cursor_in.close()
                conn.close()
            self.response.write('')
        self.response.write('')
def cron_list_high(request):
    #cada 10 min
    if request.method=='GET' and request.META['REMOTE_ADDR']=='0.1.0.1':
        CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
        DATABASE_NAME = 'oclock'
        USER_NAME = 'root'
        conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
        cursor=conn.cursor()
        cursor_in=conn.cursor()
        cursor.execute('SELECT u.users_name,u.users_email,e.events_id,e.events_title,e.events_title_id from events_high e left join users u on u.users_id = e.fk_user_creator where e.events_type=2 AND TIMESTAMPDIFF(minute,NOW(),e.events_finish) <= 10')
        ms=Mandrill_Services()
        for (users_name,users_email,events_id,events_title,events_title_id) in cursor:
            cursor_in.execute('SELECT u.users_name as users_name_sub,u.users_email as users_email_sub FROM users_follows_events ufe LEFT JOIN users u ON u.users_id=ufe.fk_users WHERE fk_events=%s;',(events_id,))
            for (users_name_sub,users_email_sub) in cursor_in:
                if users_email!=users_email_sub:
                    template_values={'events_title':events_title,'events_title_id':events_title_id}
                    t=loader.get_template('oclock/mail/clock_finished_sub_after_beta.html')
                    c=RequestContext(request,template_values)
                    #c=Context(template_values)
                    html=t.render(c)
                    ms.send_mail(users_email_sub,'It\'s time for '+events_title,html)
            template_values={'events_title':events_title,'events_title_id':events_title_id}
            t=loader.get_template('oclock/mail/clock_finished_after_beta.html')
            c=RequestContext(request,template_values)
            html=t.render(c)
            ms.send_mail(users_email,'It\'s time for '+events_title,html)
            cursor.execute('DELETE FROM events_high where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 10')
        #cursor.execute('SELECT * FROM hashtags WHERE hashtags_id<=500')
        #for (hashtags_id,hashtags_value) in cursor.fetchall():
        #    cursor_in('UPDATE hashtags SET hashtags_value=%s WHERE hashtags_id=%s',(slugify(hashtags_value.replace('?', ' ').strip()),hashtags_id))
        conn.commit()
        cursor.execute('SELECT seq_value FROM _sequence_cron WHERE seq_name="cron_facebook"')
        fq=cursor.fetchone()
        if fq is not None:
            qw=get_p(fq[0])
            cursor.execute('SELECT fk_users,social_networks_token FROM social_networks ORDER BY fk_users LIMIT %s,%s',(qw[0],qw[1]))
            if cursor.rowcount>0:
                cursor_in.execute('UPDATE _sequence_cron SET seq_value=%s WHERE seq_name="cron_facebook"',(int(fq[0])+1,))
            else:
                cursor_in.execute('UPDATE _sequence_cron SET seq_value=%s WHERE seq_name="cron_facebook"',(1,))
                
            for (fk_users,social_networks_token) in cursor:
                profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+urllib.urlencode(dict(access_token=social_networks_token))))
                #{"username": "carriagadad", "first_name": "Carlos", "last_name": "Arriagada Devia", "middle_name": "Andr\u00e9s", "name": "Carlos Andr\u00e9s Arriagada Devia", "locale": "en_US", "gender": "male", "verified": true, "email": "hackreader@hotmail.com", "link": "https://www.facebook.com/carriagadad", "timezone": -4, "updated_time": "2014-07-17T04:25:00+0000", "id": "1088104827"}"""
                friends=json.load(urllib.urlopen("https://graph.facebook.com/me/friends?"+urllib.urlencode(dict(access_token=social_networks_token))))
                #data": [{"name": "Wanting Qu", "id": "502500281"}, {"name": "S\u00edlvia Soares Boyer", "id": "509598243"}, {"name": "Luz Lopez", "id": "514874152"}"""
                #interests=json.load(urllib.urlopen("https://graph.facebook.com/me/interests?"+urllib.urlencode(dict(access_token=social_networks_token))))
                likes=json.load(urllib.urlopen("https://graph.facebook.com/me/likes?"+urllib.urlencode(dict(access_token=social_networks_token))))
                #data":[{"category": "Musician/band", "created_time": "2014-04-27T04:18:24+0000", "name": "Official Assemblage 23", "id": "138651156153800"}, {"category": "Musician/band", "created_time": "2014-04-27T04:17:52+0000", "name": "Coldplay", "id": "15253175252"}, {"category": "Radio station", "created_time": "2014-04-17T22:42:03+0000", "name": "MusicaAnimes", "id": "279689688780026"}, {"category": "Aerospace/defense", "created_time": "2014-04-14T17:50:51+0000", "name": "NASA - National Aeronautics and Space Administration", "id": "54971236771"},]"""
                events=json.load(urllib.urlopen("https://graph.facebook.com/me/events?"+urllib.urlencode(dict(access_token=social_networks_token))))
                #data": [{"name": "2da junta Hunter X Chile", "rsvp_status": "attending", "start_time": "2014-08-09T14:30:00-0400", "location": "Serrano 74, Santiago", "timezone": "America/Santiago", "id": "602653779831802", "end_time": "2014-08-09T19:30:00-0400"}, {"name": "LOCOMOTION (GRATIS): HUNTER X HUNTER THE LAST MISSION", "rsvp_status": "attending", "start_time": "2014-08-02T17:00:00-0500", "location": "AUDITORIO DE LA UPT ( centro)", "timezone": "America/Lima", "id": "1462547874012560", "end_time": "2014-08-02T20:00:00-0500"}]}"""
                #access_token_json=json.load(urllib.urlopen("https://graph.facebook.com/debug_token?"+urllib.urlencode(dict(input_token=serializer.object.social_networks_token))+"&"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
                
                ttp=profile.get("id",0)
                if ttp==0:
                    continue
                
                img=urllib2.urlopen(urllib2.Request('https://graph.facebook.com/'+profile["id"]+'/picture?type=large'),timeout=120)
                cursor_in.execute('SELECT users_path_local_avatar from users where users_path_local_avatar=%s and users_id=%s',(img.geturl(),fk_users))
                upla=cursor_in.fetchone()
                if upla==None:
                    file_name_hash=remote_image(img)                    
                    cursor_in.execute('UPDATE users SET users_path_web_avatar=%s,users_path_local_avatar=%s WHERE users_id=%s',('https://'+file_name_hash[7:],img.geturl(),fk_users))
                    
                for hash in likes.get('data',[]):
                    if hash['name'].strip()!="":
                        hash_str=hash['name'].strip()
                        hash_val=slugify(hash['name'].replace('?', ' ').strip())
                        
                        cursor_in.execute('select hashtags_id from hashtags where hashtags_value=%s',(hash_val,))
                        h=cursor_in.fetchone()
                        
                        if h==None:
                            cursor_in.execute('INSERT INTO hashtags(hashtags_value,hashtags_value_str) VALUES(%s,%s)',(hash_val,hash_str))
                            cursor_in.execute('SELECT hashtags_id FROM hashtags where hashtags_value=%s',(hash_val,))
                            h=cursor_in.fetchone()                
                        #cursor_in.execute("""select if (exists(select users_has_hashtags_id from users_has_hashtags where fk_users=%s and fk_hashtags=%s),(select hashtags_id from users_has_hashtags where fk_users=%s and fk_hashtags=%s),0)""",(fk_users,h,fk_users,h))
                        cursor_in.execute('SELECT users_has_hashtags_id FROM users_has_hashtags WHERE fk_users=%s and fk_hashtags=%s',(fk_users,h))
                        uhh=cursor_in.fetchone()
                        if uhh==None:
                            cursor_in.execute('INSERT INTO users_has_hashtags(fk_users,fk_hashtags) VALUES(%s,%s)',(fk_users,h))
                
                for event in events.get('data',[]):
                    #logging.debug(event['id'])
                    #pendiente obtener la zona horaria de timezone
                    if event.get('timezone',False)!=False:
                        try:
                            local=event['start_time']
                            #z=Zone.objects.get(zone_name__icontains=event['timezone'])
                            #datetime.datetime.now() ValueError: invalid literal for int() with base 10: '2014-08-06 23:02:52.163880'
                            #tz=Timezone.objects.filter(zone_id=z.zone_id,time_start__lte=datetime.now()).order_by('-time_start')[:1]
                            #start_t=event['start_time']+timedelta(seconds=tz.gmt_offset) 
                            #gmt_offset seconds
                            from_zone=tz.gettz(event.get('timezone','UTC'))
                            to_zone=tz.gettz('UTC')
                            if len(event['start_time'])<=10: #0000-00-00
                                local=datetime.strptime(event['start_time'],'%Y-%m-%d')
                            if len(event['start_time'])==19: #0000-00-00T00:00:00
                                local=datetime.strptime(event['start_time'],'%Y-%m-%dT%H:%M:%S')
                            if len(event['start_time'])>19: #0000-00-00T00:00:00
                                local=datetime.strptime(event['start_time'][:-5],'%Y-%m-%dT%H:%M:%S')
                            local=local.replace(tzinfo=from_zone)
                            utc=local.astimezone(to_zone)
                            start_t=utc.strftime("%Y-%m-%d %H:%M:%S") #event['start_time']
                        except ValueError:
                            continue
                    else:
                        try:
                            if len(event['start_time'])<=19: #0000-00-00 or 2012-04-07T11:00:00
                                start_t=event['start_time']
                            else:
                                if event['start_time'][-5:-4]=='-':
                                    start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")-timedelta(hours=int(event['start_time'][-4:-2]))
                                else:
                                    start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")+timedelta(hours=int(event['start_time'][-4:-2]))
                        except ValueError:
                            continue
                    opener = urllib2.build_opener()
                    opener.addheaders = [('', '')]
                    event_json={}
                    try: 
                        res=opener.open('https://graph.facebook.com/'+event['id']+'?'+urllib.urlencode(dict(access_token=social_networks_token)),None,60)
                        j = res.read()
                        event_json=json.loads(j)
                        #event_json['privacy'] OPEN-SECRET-FRIENDS
                        #event_json['owner']['id']
                    except urllib2.HTTPError, err:
                        pass
                    if event_json.get('privacy','')=='OPEN':
                        #https://graph.facebook.com/1462547874012560/picture?type=large
                        #events=Events.objects.get(events_fb_event_id=event['id'])
                        cursor_in.execute('SELECT events_id FROM events WHERE events_fb_event_id=%s',(event['id'],))
                        ev_id=cursor_in.fetchone()
                        if ev_id==None:
                            try:
                                opener = urllib2.build_opener()
                                opener.addheaders = [('', '')]
                                file_name_hash=None
                                try: 
                                    res=opener.open('https://graph.facebook.com/fql?'+urllib.urlencode(dict(q='SELECT pic_cover FROM event WHERE eid='))+event['id']+'&'+urllib.urlencode(dict(access_token=social_networks_token)),None,60)
                                    j = res.read()
                                    event_images=json.loads(j)
                                    if event_images['data'][0]['pic_cover'] is not None:
                                        img=urllib2.urlopen(event_images['data'][0]['pic_cover']['source'])
                                        file_name_hash=remote_image(img)
                                except urllib2.HTTPError, err:
                                    pass
                                if file_name_hash is not None:
                                    file_name_hash=file_name_hash
                                events_title_id=event['name']
                                e_title=event['name'].replace('-', ' ').strip()
                                e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                                e_title=slugify(e_title)
                                if len(e_title.strip())==0:
                                    e_title='oclock';
                                #verificar si existe
                                #n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                                cursor_in.execute("SELECT COUNT(*) FROM events WHERE events_title_id LIKE '%"+e_title+"'")
                                n_title=cursor_in.fetchone()
                                if n_title[0] > 0:
                                    events_title_id=e_title+'-'+str(n_title[0])
                                else:
                                    events_title_id=e_title
                            
                                if profile["id"]==event_json['owner']['id']:
                                    cursor_in.execute('INSERT INTO events(events_title,events_finish,events_skins,events_type,events_velocity,events_level,events_delete,events_enable,fk_user_creator,events_title_id,events_image,events_fb_event_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(event['name'],start_t,'skin1',2,1000,1,0,1,fk_users,events_title_id,file_name_hash,event['id']))
                                else:
                                    cursor_in.execute('INSERT INTO events(events_title,events_finish,events_skins,events_type,events_velocity,events_level,events_delete,events_enable,fk_user_creator,events_title_id,events_image,events_fb_event_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(event['name'],start_t,'skin1',2,1000,1,0,1,113,events_title_id,file_name_hash,event['id']))
                                #cursor_in.execute("SELECT events_id FROM events WHERE events_title_id LIKE '%"+events_title_id+"'")
                                #e_id=conn.insert_id()#cursor_in.fetchone()[0]
                                e_id=cursor_in.lastrowid
                                cursor_in.execute('INSERT INTO events_from_facebook(fk_users,fk_events,events_from_facebook_date) VALUES(%s,%s,%s)',(fk_users,e_id,datetime.now()))
                            except KeyError:
                                pass
                        else:
                            try:
                                #ev_id=str(ev_id)
                                events_finish=start_t
                                events_title=event['name']
                                #events.events_image=file_name_hash
                                if profile["id"]==event_json['owner']['id'] and fk_users is not None:
                                    cursor_in.execute('UPDATE events SET events_finish=%s,events_title=%s,fk_user_creator=%s WHERE events_id=%s',(events_finish,events_title,fk_users,ev_id))
                                cursor_in.execute('UPDATE events SET events_finish=%s,events_title=%s WHERE events_id=%s',(events_finish,events_title,ev_id))
                                cursor_in.execute('SELECT COUNT(*) FROM events_from_facebook WHERE fk_users=%s AND fk_events=%s',(fk_users,ev_id))
                                nnz=cursor_in.fetchone()[0]
                                if nnz<=0:
                                    cursor_in.execute('INSERT INTO events_from_facebook(fk_users,fk_events) VALUES(%s,%s)',(fk_users,ev_id))
                                cursor_in.execute('SELECT fk_users,fk_events FROM users_follows_events WHERE fk_users=%s AND fk_events=%s',(fk_users,ev_id))
                                ufe=cursor_in.fetchone()
                                if ufe==None:                        
                                    cursor_in.execute('INSERT INTO users_follows_events(fk_users,fk_events,users_follows_events_subscription_date) VALUES(%s,%s,%s)',(fk_users,ev_id,datetime.now()))
                            except KeyError:
                                pass
                #cursor_in.execute('DELETE FROM users_has_friends WHERE fk_user_from=%s',(fk_users,))
                for friend in friends.get('data',[]):
                    cursor_in.execute('SELECT users_id FROM users WHERE users_fb_id=%s',(friend['id'],))
                    uuf=cursor_in.fetchone()
                    if uuf is not None:
                        cursor_in.execute('SELECT COUNT(*) FROM users_has_friends WHERE (fk_user_from=%s AND fk_user_to=%s) OR (fk_user_from=%s AND fk_user_to=%s) ',(fk_users,uuf,uuf,fk_users))
                        ff=cursor_in.fetchone()
                        if ff[0]==0:
                            cursor_in.execute('INSERT INTO users_has_friends(fk_user_from,fk_user_to) VALUES(%s,%s)',(fk_users,uuf))
                time.sleep(5)
        
        cursor.close()
        cursor_in.close()
        conn.commit()
        conn.close()
        return HttpResponse('')
    return HttpResponse('')
class CronListLow(webapp2.RequestHandler):
    def get(self):
        if self.request.remote_addr=='0.1.0.1':
            CLOUDSQL_INSTANCE='festive-ally-585:oclock'
            DATABASE_NAME='oclock'
            USER_NAME='root'
            conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
            cursor=conn.cursor()
            cursor_in=conn.cursor()
            cursor.execute('INSERT INTO events_medium (SELECT * from events_low where events_type=2 AND TIMESTAMPDIFF(DAY,NOW(),events_finish) <= 0);')
            cursor.execute('DELETE FROM events_low WHERE events_type=2 AND TIMESTAMPDIFF(DAY,NOW(),events_finish) <= 0;')
            cursor.execute('INSERT INTO events_high (SELECT * from events_low where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 20);')
            cursor.execute('DELETE FROM events_low WHERE events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 20')
            cursor.close()
            conn.commit()
            conn.close()
            self.response.write('')
        self.response.write('')

def cron_list_low(request):
    #cada 1 dia
    if request.method=='GET' and request.META['REMOTE_ADDR']=='0.1.0.1':
        CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
        DATABASE_NAME = 'oclock'
        USER_NAME = 'root'
        conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
        cursor=conn.cursor()
        cursor_in=conn.cursor()
        cursor.execute('INSERT INTO events_medium (SELECT * from events_low where events_type=2 AND TIMESTAMPDIFF(DAY,NOW(),events_finish) <= 0);')
        cursor.execute('DELETE FROM events_low WHERE events_type=2 AND TIMESTAMPDIFF(DAY,NOW(),events_finish) <= 0;')
        
        cursor.execute('INSERT INTO events_high (SELECT * from events_low where events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 20);')
        cursor.execute('DELETE FROM events_low WHERE events_type=2 AND TIMESTAMPDIFF(MINUTE,NOW(),events_finish) <= 20')
        
        cursor.close()
        conn.commit()
        conn.close()
        return HttpResponse('')
    return HttpResponse('')
"""def create(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            #{"username": "carriagadad", "first_name": "Carlos", "last_name": "Arriagada Devia", "middle_name": "Andr\u00e9s", "name": "Carlos Andr\u00e9s Arriagada Devia", "locale": "en_US", "gender": "male", "verified": true, "email": "hackreader@hotmail.com", "link": "https://www.facebook.com/carriagadad", "timezone": -4, "updated_time": "2014-07-17T04:25:00+0000", "id": "1088104827"}
            #friends=json.load(urllib.urlopen("https://graph.facebook.com/me/friends?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            #data": [{"name": "Wanting Qu", "id": "502500281"}, {"name": "S\u00edlvia Soares Boyer", "id": "509598243"}, {"name": "Luz Lopez", "id": "514874152"}
            #interests=json.load(urllib.urlopen("https://graph.facebook.com/me/interests?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            #likes=json.load(urllib.urlopen("https://graph.faminutescebook.com/me/likes?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            #data":[{"category": "Musician/band", "created_time": "2014-04-27T04:18:24+0000", "name": "Official Assemblage 23", "id": "138651156153800"}, {"category": "Musician/band", "created_time": "2014-04-27T04:17:52+0000", "name": "Coldplay", "id": "15253175252"}, {"category": "Radio station", "created_time": "2014-04-17T22:42:03+0000", "name": "MusicaAnimes", "id": "279689688780026"}, {"category": "Aerospace/defense", "created_time": "2014-04-14T17:50:51+0000", "name": "NASA - National Aeronautics and Space Administration", "id": "54971236771"},]
            #events_json=json.load(urllib.urlopen("https://graph.facebook.com/me/events?"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            #data": [{"name": "2da junta Hunter X Chile", "rsvp_status": "attending", "start_time": "2014-08-09T14:30:00-0400", "location": "Serrano 74, Santiago", "timezone": "America/Santiago", "id": "602653779831802", "end_time": "2014-08-09T19:30:00-0400"}, {"name": "LOCOMOTION (GRATIS): HUNTER X HUNTER THE LAST MISSION", "rsvp_status": "attending", "start_time": "2014-08-02T17:00:00-0500", "location": "AUDITORIO DE LA UPT ( centro)", "timezone": "America/Lima", "id": "1462547874012560", "end_time": "2014-08-02T20:00:00-0500"}]}
            #access_token_json=json.load(urllib.urlopen("https://graph.facebook.com/debug_token?"+urllib.urlencode(dict(input_token=serializer.object.social_networks_token))+"&"+urllib.urlencode(dict(access_token=serializer.object.social_networks_token))))
            ttp=profile.get("id",0)
            if ttp==0:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            profile_id=str(profile["id"])
            profile_name=profile["name"]
            profile_link=profile["link"]
            #https://graph.facebook.com/coke.alejandro/picture?type=large
            file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
            #file_name=files.blobstore.create(mime_type='application/octet-stream',_blobinfo_uploaded_filename=file_name_hash)
            #res=opener.open(event_images['data'][0]['pic_cover']['source'],None,60)
            img=urllib2.urlopen('https://graph.facebook.com/'+profile["id"]+'/picture?type=large')
            #bin_img=res.read()
            #with bin_img as f:
            with files.open(file_name,'ab') as f:
                while True:
                    chunk=img.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            #files.open(file_name,'ab',bin_img)
            files.finalize(file_name)
            blob_key = files.blobstore.get_blob_key(file_name)
            blob_info = BlobInfo.get(blob_key)
            file_name_hash=images.get_serving_url(blob_key,size=500)
            try:
                u=Users.objects.get(users_email=profile["email"])
                #u.users_path_web_avatar='https://'+file_name_hash[7:]
                u.users_fb_id=profile["id"]
                u.users_time_zone=profile.get('timezone',None)
                u.users_locale=profile.get('locale',None)
                u.users_middle_name=profile.get('middle_name',None)
                u.users_name_id=profile.get("username",profile["id"])
                u.save()
            except Users.DoesNotExist:
                pass_hash=hashlib.sha1(str(random.uniform(1, 999999))+str(time.time())).hexdigest()
                Users(users_firstname=profile.get("first_name",None),users_lastname=profile.get("last_name",None),users_name=profile.get("name",None),users_name_id=profile.get("username",profile["id"]),users_email=profile["email"],users_password=pass_hash,fk_users_type=UsersType.objects.get(users_type_id=1),users_delete=0,users_sex=profile["gender"],users_fb_id=profile["id"],users_path_web_avatar=file_name_hash,users_date_joined=time.strftime('%Y-%m-%d %H:%M:%S'),users_time_zone=profile.get('timezone',None),users_locale=profile.get('locale',None),users_middle_name=profile.get('middle_name',None)).save()
                u=Users.objects.get(users_email=profile["email"])
                c=Client(user_id=u.users_id,name=u.users_email,url='',redirect_uri='',client_id='02770b9b0452d7e56a1d',client_secret='0b671033626580921b56593440c3e387d0cb5ec6',client_type=1).save()
            else:
                u=Users.objects.get(users_email=profile["email"])
                pass_hash=u.users_password
            for hash in likes['data']:
                try:
                    hashtag=Hashtags.objects.get(hashtags_value=hash['name'])
                except Hashtags.DoesNotExist:
                    hashtag=Hashtags(hashtags_value=hash['name']).save()
                    hashtag=Hashtags.objects.get(hashtags_value=hash['name'])
                try:
                    uhhashtag=UsersHasHashtags.objects.get(fk_users=u,fk_hashtags=hashtag)
                except UsersHasHashtags.DoesNotExist:
                    uhhashtag=UsersHasHashtags(fk_users=u,fk_hashtags=hashtag)
                    uhhashtag.save()
            for event in events_json['data']:
                #pendiente obtener la zona horaria de timezone
                if event.get('timezone',False) != False:
                    local=event['start_time']
                    #z=Zone.objects.get(zone_name__icontains=event['timezone'])
                    #datetime.datetime.now() ValueError: invalid literal for int() with base 10: '2014-08-06 23:02:52.163880'
                    #tz=Timezone.objects.filter(zone_id=z.zone_id,time_start__lte=datetime.now()).order_by('-time_start')[:1]
                    #start_t=event['start_time']+timedelta(seconds=tz.gmt_offset) 
                    #gmt_offset seconds
                    from_zone=tz.gettz(event.get('timezone','UTC'))
                    to_zone=tz.gettz('UTC')
                    if len(event['start_time'])<=10: #0000-00-00
                        local=datetime.strptime(event['start_time'],'%Y-%m-%d')
                    if len(event['start_time'])==19: #0000-00-00T00:00:00
                        local=datetime.strptime(event['start_time'],'%Y-%m-%dT%H:%M:%S')
                    if len(event['start_time'])>19: #0000-00-00T00:00:00
                        local=datetime.strptime(event['start_time'][:-5],'%Y-%m-%dT%H:%M:%S')
                    local=local.replace(tzinfo=from_zone)
                    utc=local.astimezone(to_zone)
                    start_t=utc.strftime("%Y-%m-%d %H:%M:%S") #event['start_time']
                else:
                    if len(event['start_time'])<=19: #0000-00-00 or 2012-04-07T11:00:00
                        start_t=event['start_time']
                    else:
                        if event['start_time'][-5:-4]=='-':
                            start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")-timedelta(hours=int(event['start_time'][-4:-2]))
                        else:
                            start_t=datetime.strptime(event['start_time'][:-5], "%Y-%m-%dT%H:%M:%S")+timedelta(hours=int(event['start_time'][-4:-2]))
                
                opener = urllib2.build_opener()
                opener.addheaders = [('', '')]
                event_json={}
                try: 
                    res=opener.open('https://graph.facebook.com/'+event['id']+'?'+urllib.urlencode(dict(access_token=serializer.object.social_networks_token)),None,60)
                    j = res.read()
                    event_json=json.loads(j)
                    #event_json['privacy'] OPEN-SECRET-FRIENDS
                    #event_json['owner']['id']
                except urllib2.HTTPError, err:
                    pass
                if event_json.get('privacy','')=='OPEN':
                    try:
                        #https://graph.facebook.com/1462547874012560/picture?type=large
                        events=Events.objects.get(events_fb_event_id=event['id'])
                        events.events_finish=start_t
                        events.events_title=event['name']
                        #events.events_image=file_name_hash
                        if profile["id"]==event_json['owner']['id']:
                            events.fk_user_creator=u
                        events.save()
                        try:
                            ufe=UsersFollowsEvents.objects.get(fk_users=u,fk_events=events)
                        except UsersFollowsEvents.DoesNotExist:
                            ufe=UsersFollowsEvents(fk_users=u,fk_events=events).save()
                    except Events.DoesNotExist:
                        opener = urllib2.build_opener()
                        opener.addheaders = [('', '')]
                        file_name_hash=None
                        try: 
                            res=opener.open('https://graph.facebook.com/fql?'+urllib.urlencode(dict(q='SELECT pic_cover FROM event WHERE eid='))+event['id']+'&'+urllib.urlencode(dict(access_token=serializer.object.social_networks_token)),None,60)
                            j = res.read()
                            event_images=json.loads(j)
                            if event_images['data'][0]['pic_cover'] is not None:
                                file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
                                file_name=files.blobstore.create(mime_type='application/octet-stream',_blobinfo_uploaded_filename=file_name_hash)
                                #res=opener.open(event_images['data'][0]['pic_cover']['source'],None,60)
                                img=urllib2.urlopen(event_images['data'][0]['pic_cover']['source'])
                                #bin_img=res.read()
                                #with bin_img as f:
                                with files.open(file_name,'ab') as f:
                                    while True:
                                        chunk=img.read(8192)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                #files.open(file_name,'ab',bin_img)
                                files.finalize(file_name)
                                blob_key = files.blobstore.get_blob_key(file_name)
                                blob_info = BlobInfo.get(blob_key)
                                file_name_hash=images.get_serving_url(blob_key,size=600)
                        except urllib2.HTTPError, err:
                            pass
                        events_title_id=event['name']
                        e_title=event['name'].replace('-', ' ').strip()
                        e_title=" ".join(e_title.split()) #elimina espacios fuera y dobles dentro
                        e_title=slugify(e_title)
                        if len(e_title.strip())==0:
                            e_title='oclock'; 
                        #verificar si existe
                        n_title=Events.objects.filter(events_title_id__istartswith=str(e_title)).count()
                        if n_title > 0: 
                            events_title_id=e_title+'-'+str(n_title)
                        else:
                            events_title_id=e_title
                        if profile["id"]==event_json['owner']['id']:
                            ee=Events(events_title=event['name'],events_finish=start_t,events_skins='skin1',events_type=2,events_velocity=1000,events_level=1,events_delete=0,events_enable=1,fk_user_creator=u,events_title_id=events_title_id,events_image=file_name_hash,events_fb_event_id=event['id']).save()
                        else:
                            u=Users.objects.get(users_id=1) #usuario 1 es de sistema
                            ee=Events(events_title=event['name'],events_finish=start_t,events_skins='skin1',events_type=2,events_velocity=1000,events_level=1,events_delete=0,events_enable=1,fk_user_creator=u,events_title_id=events_title_id,events_image=file_name_hash,events_fb_event_id=event['id']).save()
                    #opener = urllib2.build_opener()
                    #opener.addheaders = [('', '')]
                    #try: 
                    #    res=opener.open(events_json['paging']['next'],None,60)
                    #    j = res.read()
                    #    events_json=json.loads(j)
                    #    if len(events_json['data'])<=0:
                    #        break
                    #except urllib2.HTTPError, err:
                    #    break
            serializer.object.fk_users=u
            serializer.object.users_network_id=profile["id"]
            serializer.object.social_networks_enable=1
            #if access_token_json.get("data",False)!=False:
                #serializer.object.social_networks_expires_in=access_token_json["data"].get("expires_at","0")
            #else:
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
                return Response(j_obj,status=status.HTTP_201_CREATED,headers=headers)
            except urllib2.HTTPError, err:
                if err.code == 404:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""