from rest_framework.serializers import ModelSerializer
from auth_api.models import User,SignupRequest
from rest_framework import serializers


class UserSerializer(ModelSerializer):
   class Meta:
      model = User
      fields = ['email','full_name','mobile_no','region','password']
      extra_kwargs = {
         'password' : {'write_only' : True}
      }


   


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()



class SignUpRequestSerilizer(ModelSerializer):
   class Meta:
      model = SignupRequest
      fields = ['email','full_name','mobile_no','region','password']