'''
Created on 13-01-2015

@author: carriagadad
'''
from oclock.apps.media.images import get_size,init_image,remote_image
from google.appengine.api import files
from django.http import HttpResponse
import hashlib
import time
import json
import urllib2
from PIL import Image
from google.appengine.api import rdbms
#import logging
def get_p(p,c=60):
    r=[]
    r_by_p=c
    l_l=(p-1)*r_by_p
    r.append(l_l)
    r.append(r_by_p)
    return r
def test_image(request):
    if request.method=='POST':
        val=request.REQUEST.get('o','10')
        pag=int(request.REQUEST.get('p',1))
        p=get_p(pag)
        if val=='1':
            try:
                CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
                DATABASE_NAME = 'oclock'
                USER_NAME = 'root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c2=conn.cursor()
                c.execute('SELECT events_id,events_image FROM events WHERE events_id>4188 AND events_image not like %s ORDER BY events_id LIMIT %s,%s',("%storage.googleapis.com%",p[0],p[1]))
                for o in c.fetchall():
                    if o[1] is not None and o[1]!='':
                        file_obj=urllib2.urlopen(urllib2.Request(o[1]),timeout=120)
                        img=remote_image(file_obj)
                        c2.execute('UPDATE events SET events_image=%s WHERE events_id=%s',(img,o[0]))
                        conn.commit()
                #file_obj=urllib2.urlopen('https://lh4.ggpht.com/8rzLyu0eLxf54WgxNwjX33jjbwsWhvRbl68MyiJdJyn2-CHqSOwCo8hQIxU_nVJB-ZgHqYSQrGv9Lp9DZCoFozMRP1ovS3M=s500')
                c.close()
                c2.close()
                conn.close()
                return HttpResponse('1')
            except urllib2.HTTPError,err:
                #file_obj=request.FILES['image']
                return HttpResponse(err)
        elif val=='2':
            try:
                CLOUDSQL_INSTANCE = 'festive-ally-585:oclock'
                DATABASE_NAME = 'oclock'
                USER_NAME = 'root'
                conn=rdbms.connect(instance=CLOUDSQL_INSTANCE,database=DATABASE_NAME,user=USER_NAME,charset='utf8')
                c=conn.cursor()
                c2=conn.cursor()
                c.execute('SELECT users_id,users_path_web_avatar FROM users WHERE users_path_web_avatar NOT LIKE %s LIMIT %s,%s',("%storage.googleapis.com%",p[0],p[1]))
                for o in c.fetchall():
                    if o[1] is not None:
                        file_obj=urllib2.urlopen(urllib2.Request(o[1]),timeout=120)
                        img=remote_image(file_obj)
                        c2.execute('UPDATE users SET users_path_web_avatar=%s WHERE users_id=%s',(img,o[0]))
                        conn.commit()
                #file_obj=urllib2.urlopen('https://lh4.ggpht.com/8rzLyu0eLxf54WgxNwjX33jjbwsWhvRbl68MyiJdJyn2-CHqSOwCo8hQIxU_nVJB-ZgHqYSQrGv9Lp9DZCoFozMRP1ovS3M=s500')
                c.close()
                c2.close()
                conn.close()
                return HttpResponse('2')
            except urllib2.HTTPError,err:
                #file_obj=request.FILES['image']
                return HttpResponse(err)
            return HttpResponse('')
        else:
            file_obj=init_image(request.FILES['image'])
            return HttpResponse(file_obj)
        return HttpResponse('')
    if request.method=='GET':
        return HttpResponse('0:tamaño<br/>1:aspecto<br/>2:tipo<br/>3:peso<br/><form action="/tests/upload_image" method="post" enctype="multipart/form-data"><input type="file" name="image"/><input type="submit" value="enviar"/></form>')
    return HttpResponse('')