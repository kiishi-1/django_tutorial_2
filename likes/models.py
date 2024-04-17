from django.conf import settings
from django.db import models
# from django.contrib.auth.models import User
# default user class from the auth system
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class LikedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

#in django we use migrations to create or update our datebase tables
#based of the models we have in our project
#in django we are not going to manually create or modify our datbase tables
#django will take care of it
#after making changes to you models you should make migrations and migrate


#python manage.py makemigration
#with this django will check all the installed apps and 
#create migration files for each app

# running the migrate command python manage.py migrate, will generate a table for an app