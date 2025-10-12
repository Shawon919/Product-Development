from django.urls import path,include
from . import views

urlpatterns = [
    
    path('signup/',views.RegitrarionApiView.as_view(),name='signup'),
    path("verify-email/<int:uid>/<str:token>/",views.VerifyUser.as_view(), name="verify-email"),
    path('login/', views.GoogleLoginAPIView.as_view(), name='google-login'),
    
]