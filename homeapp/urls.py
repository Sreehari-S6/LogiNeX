from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import logout_view

urlpatterns = [
    path('',views.loadindex,name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('company_registration/', views.company_register, name='company_register'),
    path("logout/", logout_view, name="logout"),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('forgot-password/', views.forgot_password, name="forgot_password"),
path('verify-otp/', views.verify_otp, name="verify_otp"),
path('reset-password/', views.reset_password, name="reset_password"),
    
]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 