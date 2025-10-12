import requests
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from . import serializers
from django.contrib.auth import get_user_model
from .utils import email_verification_token
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404



User = get_user_model()

class GoogleLoginAPIView(APIView):
    def post(self,request):
        access_token = request.data.get('access_token')

        if not access_token:
            return Response({
                'error' : 'Access token is required'
            },status=status.HTTP_400_BAD_REQUEST)
        
        try:
            google_response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers= {
                    'Authorization' : f'Bearer {access_token}'
                })
            
        except requests.exceptions.RequestException as e:
            return Response({
                'error' : 'Failed to fetch user info from Google',
                'details' : str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

        if google_response.status_code != 200:
            return Response({
                'error' : 'Invalid access token'
            },status=status.HTTP_401_UNAUTHORIZED)
        

        response = google_response.json()

        email = response.get('email')
        username = response.get('name')

        if not email:
            return Response({
                'error' : ' Email is not registered with google'
            },status=status.HTTP_400_BAD_REQUEST)
        

        user,created = User.objects.get_or_create(email=email,defaults={'username' : username})

        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        return Response({
            'message' : 'User logged in successfully',
            'user' : {
                'username' : user.username,
                'email' : user.email
            },
            'tokens' : {
                'refresh' : str(refresh_token),
                'access' : access_token
            }
        },status=status.HTTP_200_OK)



class SetPasswordAPIView(APIView):
    def post(self,request):
        user = request.user
        new_password = request.data.get('new_password')

        if not new_password:
            return Response({
                'error' : 'New password is required'
            },status = status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()

        return Response({
            'message' : 'Password updated successfully'
        },status=status.HTTP_200_OK)
    



class RegitrarionApiView(APIView):
    def post(self,request):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
           
           email = serializer.validated_data['email']
           if User.objects.filter(email=email).exists():
             return Response({
                "error" : "This email has already been taken"
            },status=status.HTTP_400_BAD_REQUEST)
           
           user = serializer.save()
           
           

           token = email_verification_token.make_token(user)
           uid = user.pk   
           current_site = get_current_site(request).domain
           
           
           link = f'http://{current_site}/varify-email/{uid}/{token}'
           

           send_mail(
            subject =  f"Click this link to verify your email : {link}",
            message =  "Email Varification",
            from_email = f"the email is from {settings.EMAIL_HOST_USER}",
            recipient_list = [email],
            fail_silently = False
        )

           return Response({"message": "User registered. Check your email to verify.",'serializer':serializer.data}, status=201)
        

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyUser(APIView):
    def post(self,uid,token):
       user= get_object_or_404(User,pk=uid)
       if email_verification_token.check_token(user,token):
           user.is_active = True
           user.save()
           refreshtoken = RefreshToken.for_user(user)
           access_token = refreshtoken.access_token
           return Response({
               "message" : "varified successfull",
               "accestoken" : str(access_token),
               "refreshtoken" : str(refreshtoken)
           })
       return Response({"error": "Invalid or expired token."}, status=400) 





        
           

    