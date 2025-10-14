import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers
from django.contrib.auth import get_user_model
from .utils import email_verification_token
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser,UerOTP,SignupRequest
import random
from kafka.producer import producer_event
import uuid
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail


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
            

            if google_response.status_code == 200:
                info = google_response.json()
                email = info.get("email")
                name = info.get('name')
                user_info = User.objects.filter(email=email)
                if user_info.exists():
                   user = User.objects.get(email=email)
                   refresh = RefreshToken.for_user(user)
                   access_token = refresh.access_token

                   return Response({
                       'message' : "user is already registered,so login successfuly",
                       'access_token' : str(access_token)
                   },status=status.HTTP_200_OK)
                
                
                
                user = User.objects.create_user(email=email,full_name = name)
                user.is_active = True
                user.save()
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
                    },
                    
                },status=status.HTTP_200_OK)

            return Response(
                {
                    "error" : "google token is not valid"
                },status=status.HTTP_401_UNAUTHORIZED
            )            

            
        except requests.exceptions.RequestException as e:
            return Response({
                'error' : 'Failed to fetch user info from Google',
                'details' : str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

        
        

      

        
        

      



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
       if not  serializer.is_valid():
           return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
       

       
       email = serializer.validated_data['email']
       full_name = serializer.validated_data['full_name']
       mobile_no = serializer.validated_data['mobile_no']
       region = serializer.validated_data['region']
       password = serializer.validated_data['password']


       
       baseURL = get_current_site(request).domain
       request_id = uuid.uuid4()

       event = {
            'event_type': 'signup_request',
            'email': email,
            'full_name': full_name,
            'mobile_no': mobile_no,
            'region': region,
            'password': password,
            'base_url': baseURL,
           
        }

       try:
           producer_event("auth-topic",event)
           return Response({
                'status': 'pending',
                'request_id': request_id,
                'message': 'Signup request received. Check your email to verify your account.'
            }, status=status.HTTP_202_ACCEPTED)
       except Exception as e:
          return Response({
              'error':"kafka pusblish failed"
          },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       


    
       

            
                
    
            





class VerifyUser(APIView):
    def post(self,requset,uid,token,*args, **kwargs):
       user = get_object_or_404(User,id=uid)
       if email_verification_token.check_token(user,token):
           user.is_active = True
           user.save()
           refreshtoken = RefreshToken.for_user(user)
           access_token = refreshtoken.access_token
           return Response({
               "message" : "varified successfull",
               "accestoken" : str(access_token),
               "refreshtoken" : str(refreshtoken),
               "is_user" : user.is_active
           })
       return Response({"error": "Invalid or expired token."}, status=400) 








class LoginApiView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        if  email and password:
            user = authenticate(request,email = email,password=password)
            if user:
                token = RefreshToken.for_user(user)
                return Response({'user_details':{
                    'email': email,
                    'password':password,
                    'token':str(token.access_token)
                },
                'message':'success',
                'status': status.HTTP_202_ACCEPTED
                })
            
            return Response({"message":'email or password is invalid','status':'falid','status':'failed'},status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'message': 'somethis is wrong'
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
              
         


class ResnedVerificationEmail(APIView):
    def post(self,request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            if user:
                token = email_verification_token.make_token(user)
                current_site = get_current_site(request).domain
                link = f'http://{current_site}/auth/verify-email/{user.pk}/{token}'

                send_mail(
                    subject= "Email Verification",
                    message=f"Click here to verify your email:{link}",
                    from_email= settings.EMAIL_HOST_USER,
                    recipient_list=[email]
                )
                return Response({
                    "message" : "verification resent,check your device"
                },status=status.HTTP_201_CREATED)
            return Response({
                'message' : 'failed to send verificatin',
                'status' : 'failed'
            },status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist as e:
            return Response({
                'error' : str(e)
            })
        
 

           


class ForgetPasswordApiView(APIView):
    def post(self,request):
        email = request.data.get('email')

        if not email:
            return Response({
                "error":"email is required"
            })
        
        try:
            user_email = User.objects.get(email=email)
            otp = ''.join(str(random.randint(0,9)) for _ in range(6))
            UerOTP.objects.create(email=user_email,otp=otp)
            send_mail(
                subject="Verify your otp",
                message=f"Your otp is {otp},It will be valid for new 30 minutes",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email]

            )
            return Response({
                'message' : "email send successfully"
            },status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist as e:
            return Response({
                'error' : str(e)
            })





class OtpVerificatinApiView(APIView):
    def post(self,request):
        email = request.data.get('email')
        otp= request.data.get('otp')

        try:
            if not User.objects.filter(email=email).exists():
                return Response({
                    'user not foud'
                })
            try:
                user_info = UerOTP.objects.get(email=email)
                
            except:
                return Response({
                    "error" : "email not foud"
                })
            if str(user_info.otp).strip() == str(otp).strip():
                    user_info.delete()
                    user_p = User.objects.get(email=email)
                    refreshtoken = RefreshToken.for_user(user_p)
                    access_token = refreshtoken.access_token
                    return Response({
                        "message" : "otp matched successfully",
                        'access_token' : str(access_token),
                        'refresh_tonek' : str(refreshtoken)
                    }) 
            return Response({
                    'error' : "otp did not match"
                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        