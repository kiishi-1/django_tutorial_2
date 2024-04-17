from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# we need to create a new user model. we can't add to just any app like
# the store or playground app cus they have nothing to do with authentication
# they have there specific purpose and it has nothing to do with auth
# what we are trying to solve is something very specific
# the core app was built with combine features of other apps, so the
# code written here is very speific to this project and it is the right 
# place to add the new custom user models

# we must extend the abstract user in the authentication system

# we are going to use this class instead of the default class in
# the auth system
class User(AbstractUser):
    # it is not optimal to swap User models i.e default in the auth system
    # to custom user model in the middle of a project. so as best practice
    # we should always create a custom user model at the beginning of a project
    # you just create an empty class using the pass keyword and it'll 
    # ensure later on if you want to replace the class, you won't have issues
    
    # pass
    email = models.EmailField(unique=True)
    # we didn't have a unique constraint on the email column(field)
    # meaning we can have multiple users with the same email
    # so, we redefine the email field to cater for it
    # note: check the email column(field) in the auth_user 
    # table in the DB(in workbench) for reference

    # we need to tell django to use the custom user model instead
    # of the user class in the auth system 
    # go to settings module and define a new setting - AUTH_USER_MODEL = 'core.User'