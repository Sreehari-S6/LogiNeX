from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'LAdmin'

urlpatterns = [

    # Admin Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # View Users
    path('users/', views.view_users, name='view_users'),
    
    # View Companies
    path('companies/', views.view_companies, name='view_companies'),
    path('companies/update/', views.update_company_status, name='update_company_status'),
    path("routes/", views.manage_routes, name="manage_routes"),
    path("ships/", views.admin_view_ships, name="view_ships"),
    path(
    "reviews/",
    views.admin_view_all_reviews,
    name="view_all_reviews"
    ),

]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 