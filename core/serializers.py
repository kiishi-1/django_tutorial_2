from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        # we want the meta class to inherit everything 
        # in the meta class of the BaseUserCreateSerializer
        # the only thing we want to override is the fields attribute
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        # add 'user_create': 'core.serializers.UserCreateSerializer', to 
        # the serializer settings for djoser 

# difference btw token based authentication and JSON web token authentication
# is that it requires a Db call and JSON web token authentication doesn't
        

# access token is a short lived token used for calling secure api endpoints
# while refresh token is used to get a new access token
# by default refresh token is valid for 1 day while access token is 
# valid for 5 minutes
        
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        # add 'current_user': 'core.serializers.UserSerializer', to 
        # the serializer settings for djoser 
