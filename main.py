import django.core.handlers.wsgi
import webapp2
from oclock.apps.base.cron import CronListLow,CronListMedium,CronListHigh,CronEventsQueue

application=django.core.handlers.wsgi.WSGIHandler()

cron=webapp2.WSGIApplication([
('/taskman/jHS-sjdIaj_jabc-quyUtqalKzM-jwyh8Ja-HqY',CronListLow),
('/taskman/UyahFAtA5X-Xta6YZvxu-AzUhAjjJ-MM-98AQ_0',CronListMedium),
('/taskman/Uhagw37H-AAS_aUQhdII982-aAQqAh-W7kUjbXZ',CronListHigh),
('/taskman/JazQpOaklW-AQ-A81WEkAyqOuw-KmzALkql72-1R',CronEventsQueue)
],debug=True)