from oclock.apps.db.models import Users
def authenticate(email,password):
    try:
        user=Users.objects.get(users_email=email,users_password=password)
        return user;
    except Users.DoesNotExist:
        return None
