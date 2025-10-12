from rest_framework.serializers import ModelSerializer
from auth_api.models import User


class UserSerializer(ModelSerializer):
   class Meta:
      model = User
      fields = ['email','full_name','mobile_no','password']
      extra_kwargs = {
         'password' : {'write_only' : True}
      }

   def create(self,validated_data):
      user = User.objects.create_user(
         email = validated_data['email'],
         full_name=validated_data['full_name'],
         mobile_no = validated_data['mobile_no'],
         password = validated_data['password']
      )   

      user.is_active = False
      user.save()
      return user