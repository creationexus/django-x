'''
Created on 28-05-2014

@author: carriagadad
'''
from google.appengine.ext import db

import pickle
import base64

import json
import datetime
import re
import types

#from django.contrib import admin
#from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
from oauth2client.appengine import CredentialsProperty

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content, and date."""
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def get_key_from_name(cls, guestbook_name=None):
        return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

##GOOGLE
"""
class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass


admin.site.register(CredentialsModel, CredentialsAdmin)
"""

class Jsonifiable:
  """Base class providing convenient JSON serialization and deserialization
  methods.
  """
  jsonkind = 'photohunt#jsonifiable'

  @staticmethod
  def lower_first(key):
    """Make the first letter of a string lower case."""
    return key[:1].lower() + key[1:] if key else ''

  @staticmethod
  def transform_to_camelcase(key):
    """Transform a string underscore separated words to concatenated camel case.
    """
    return Jsonifiable.lower_first(
        ''.join(c.capitalize() or '_' for c in key.split('_')))

  @staticmethod
  def transform_from_camelcase(key):
    """Tranform a string from concatenated camel case to underscore separated
    words.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

  def to_dict(self):
    """Returns a dictionary containing property values for the current object
    stored under the property name in camel case form.
    """
    result = {}
    for p in self.json_properties():
      value = getattr(self, p)
      if isinstance(value, datetime.datetime):
        value = value.strftime('%s%f')[:-3]
      result[Jsonifiable.transform_to_camelcase(p)] = value
    return result

  def to_json(self):
    """Returns a JSON string of the properties of this object."""
    properties = self.to_dict()
    if isinstance(self, db.Model):
      properties['id'] = unicode(self.key().id())
    return json.dumps(properties)

  def json_properties(self):
    """Returns a default list properties for this object that should be
    included when serializing this object to, or deserializing it from, JSON.

    Subclasses can customize the properties by overriding this method.
    """
    attributes = []
    all = vars(self)
    for var in all:
      if var[:1] != '_':
        attributes.append(var)
    if isinstance(self, db.Model):
      properties = self.properties().keys()
      for property in properties:
        if property[:1] != '_':
          attributes.append(property)
    return attributes

  def from_json(self, json_string):
    """Sets properties on this object based on the JSON string supplied."""
    o = json.loads(json_string)
    properties = {}
    if isinstance(self, db.Model):
      properties = self.properties()
    for key, value in o.iteritems():
      property_value = value
      property_key = Jsonifiable.transform_from_camelcase(key)
      if property_key in properties.keys():
        if properties[property_key].data_type == types.IntType:
          property_value = int(value)
      self.__setattr__(property_key, property_value)
      
      
class JsonifiableEncoder(json.JSONEncoder):
  """JSON encoder which provides a convenient extension point for custom JSON
  encoding of Jsonifiable subclasses.
  """
  def default(self, obj):
    if isinstance(obj, Jsonifiable):
      result = json.loads(obj.to_json())
      return result
    return json.JSONEncoder.default(self, obj)

class DirectedUserToUserEdge(db.Model, Jsonifiable):
  """Represents friend links between PhotoHunt users."""
  owner_user_id = db.IntegerProperty()
  friend_user_id = db.IntegerProperty()

class User(db.Model, Jsonifiable):
  """Represents a PhotoHunt user."""
  jsonkind = 'photohunt#user'
  email = db.EmailProperty()
  google_user_id = db.StringProperty()
  google_display_name = db.StringProperty()
  google_public_profile_url = db.LinkProperty()
  google_public_profile_photo_url = db.LinkProperty()
  google_credentials = CredentialsProperty()

  def json_properties(self):
    """Hide google_credentials from JSON serialization."""
    properties = Jsonifiable.json_properties(self)
    properties.remove('google_credentials')
    return properties

  def get_friends(self):
    """Query the friends of the current user."""
    edges = DirectedUserToUserEdge.all().filter(
        'owner_user_id =', self.key().id()).run()
    return db.get([db.Key.from_path('User', edge.friend_user_id) for edge in
                   edges])