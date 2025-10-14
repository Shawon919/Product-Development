from django.urls import path,include
from . import views

urlpatterns = [
    
    path('signup/',views.RegitrarionApiView.as_view(),name='signup'),
    path('signin/',views.LoginApiView.as_view(),name="signin"),
    path('login/', views.GoogleLoginAPIView.as_view(), name='google-login'),
    path('verify-email/<uid>/<token>',views.VerifyUser.as_view(),name="verify-email"),
    path('resend-verification/',views.ResnedVerificationEmail.as_view(),name="resend-email"),
    path("forget-password/",views.ForgetPasswordApiView.as_view(),name="forget-password"),
    path('verify-password/',views.OtpVerificatinApiView.as_view(),name="verify-password")
    
    
]