'''
Created on 13-06-2014

@author: carriagadad
'''

#import mandrill
import logging
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
#from google.appengine.api import mail

class Mandrill_Services():
    """mandrill_client = mandrill.Mandrill('B5qyJYPbBP7aGKtegPHJXA')
    logging.debug( '%s' % mandrill_client.users.ping() )
    mail.send_mail(sender="Bot <digitaldreami@gmail.com>",
          to="Guillermo Diaz <carlos.arriagada@ibex.cl>",
          subject="Your account has been approved",
          body="
            Dear Albert:
            
            Your example.com account has been approved.  You can now visit
            http://www.example.com/ and sign in using your Google Account to
            access new features.
            
            Please let us know if you have any questions.
            
            The example.com Team
            ")"""
    def send_mail(self,to,subject,html):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = "O'Clock <noreply@oclock.com>"
        msg['To']      = to
        #text = "Mandrill speaks plaintext"
        #part1 = MIMEText(text, 'plain')
        #html = "<em>Mandrill speaks <strong>HTML</strong></em>"
        part1=MIMEText(html.encode('utf-8'),'html','utf-8')
        username=settings.MANDRILL_SMTP_USER
        password=settings.MANDRILL_SMTP_PASS
        #msg.attach(part1)
        msg.attach(part1)
        s = smtplib.SMTP('smtp.mandrillapp.com', 587)
        s.login(username, password)
        if s.sendmail(msg['From'], msg['To'], msg.as_string()):
            s.quit()
            return 0
        else:
            s.quit()
            return 1
        