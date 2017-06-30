'''
Created on 06-06-2014

@author: carriagadad
'''

from protorpc import messages

class User(messages.Message):
    """Clock ProtoRPC message

    Clock fields needed to define the schema for methods.
    """
    users_name = messages.StringField(1,required=True)
    users_lastname = messages.StringField(2,required=True)
    users_firstname = messages.StringField(3,required=True)
    users_email = messages.StringField(4,required=True)
    users_password = messages.StringField(5,required=True)
    users_path_local_avatar = messages.StringField(6,required=False)
    users_path_web_avatar = messages.StringField(7,required=False)
    users_time_zone = messages.StringField(8,required=True)
    #fk_users_type = messages.IntegerField(9,required=False) #UsersType.objects.get(users_type_id=1)
    #users_delete = messages.IntegerField(10,required=False)
    users_birthday = messages.StringField(9,required=True)
    users_sex = messages.StringField(10,required=True)

class UserLogin(messages.Message):
    users_email = messages.StringField(1,required=True)
    users_password = messages.StringField(2,required=True)
    
class UserLoginResponse(messages.Message):
    hash = messages.StringField(1,required=True)
    id = messages.StringField(2,required=True)    
    
class GetUser(messages.Message):
    id = messages.StringField(1, required=True)
    hash = messages.StringField(2, required=True)

class ClockCollection(messages.Message):
    """Collection of Clocks."""
    #books = messages.MessageField(Clock, 1, repeated=True)
    #year = messages.IntegerField(2)