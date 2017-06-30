'''
Created on 29-06-2014

@author: carriagadad
'''
# some_app/views.py
from django.views.generic import TemplateView

class CreateUserView(TemplateView):
    template_name = "oclock/create_user.html"

class LoginUserView(TemplateView):
    template_name = "oclock/login_user.html"
    
class RegisterUserView(TemplateView):
    template_name = "oclock/login_user.html"
    
class MainView(TemplateView):
    template_name = "oclock/main_page.html"
    
