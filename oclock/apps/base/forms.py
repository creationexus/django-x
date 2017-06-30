'''
Created on 29-07-2014
@author: carriagadad
'''
from django import forms
class LoginForm(forms.Form):
    email=forms.CharField()
    password=forms.CharField()
class CreateEvent(forms.Form):
    tit=forms.CharField(label='Insert the title',max_length=200)
    tp=forms.IntegerField()
    dt=forms.DateField()
    tm=forms.TimeField()
    hs1=forms.CharField(max_length=15,required=False)
    hs2=forms.CharField(max_length=15,required=False)
    hs3=forms.CharField(max_length=15,required=False)
    lat=forms.CharField(max_length=45,required=False)
    lon=forms.CharField(max_length=45,required=False)
    country=forms.CharField(max_length=45,required=False)
    fileselect=forms.FileField(required=False)
    str_img=forms.CharField(required=False)
class CreateEventChristmas(forms.Form):
    lat=forms.CharField(max_length=45,required=False)
    lon=forms.CharField(max_length=45,required=False)
    country=forms.CharField(max_length=45,required=False)
    fileselect=forms.FileField(required=False)
    friends=forms.CharField(required=True)
    str_img=forms.CharField(required=False)
    msg=forms.CharField(max_length=500,required=True)
class CreateEventValentine(forms.Form):
    lat=forms.CharField(max_length=45,required=False)
    lon=forms.CharField(max_length=45,required=False)
    country=forms.CharField(max_length=45,required=False)
    fileselect=forms.FileField(required=False)
    friends=forms.CharField(required=True)
    str_img=forms.CharField(required=False)
    msg=forms.CharField(max_length=500,required=True)
    start=forms.DateTimeField(required=True)
class FriendInvitation(forms.Form):
    email=forms.CharField(label='Insert the email',min_length=3,max_length=255)
class Event(forms.Form):
    page=forms.IntegerField(required=True)
    type=forms.CharField(max_length=9,required=True)
    id=forms.IntegerField(required=True)
    img_size=forms.IntegerField(required=False)
    search=forms.CharField(max_length=30,required=False)
    device=forms.IntegerField(min_value=0,max_value=1,required=False)
class DeleteEvent(forms.Form):
    id=forms.IntegerField(required=True)
class DeleteComment(forms.Form):
    id=forms.IntegerField(required=True)
class DraftEvent(forms.Form):
    title=forms.CharField(max_length=100,required=True)
    img_bg=forms.CharField(max_length=150,required=True)
    dateq=forms.DateField(required=False)
    type=forms.CharField(max_length=9,required=True)
    hashtag=forms.CharField(max_length=15,required=False)
    e_id=forms.IntegerField(required=True)
class UserEnableLocation(forms.Form):
    enable_location=forms.IntegerField(min_value=0,max_value=1,required=True)
class Activities(forms.Form):
    language=forms.CharField(max_length=5,required=True)
class EditEvent(forms.Form):
    e_title=forms.CharField(max_length=200,required=True)
    e_sort=forms.IntegerField(required=True)
    e_cc=forms.CharField(max_length=200,required=True)