from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'LCompany'

urlpatterns = [

    # Admin Dashboard
    path('', views.Company_Dashboard, name='Company_Dashboard'),
    path("manage_ships/", views.manage_ships, name="manage_ships"),
    path("add_ship/", views.add_ship, name="add_ship"),
    path("add_ship_route/",views.add_ship_route,name="add_ship_route"),
    path("shipping-requests/",views.view_requests,name="view_requests"),
    path("shipping-requests/update/<int:request_id>/",views.update_request_status,name="update_request_status"),
    path(
        "shipping-requests/payment/<int:request_id>/",
        views.add_shipping_payment,
        name="add_shipping_payment"   # 🔴 THIS NAME MUST MATCH
    ),
    path("reviews/", views.company_reviews, name="company_reviews"),
    path(
    "shipment-status/",
    views.update_shipment_status_page,
    name="update_shipment_status_page"
    ),

    path(
    "shipment-status/update/<int:request_id>/",
    views.update_shipment_status,
    name="update_shipment_status"
    ),
    path(
    "send-feedback/",
    views.send_feedback,
    name="send_feedback"
),
    path(
    "edit-profile/",
    views.edit_company_profile,
    name="edit_company_profile"
),


]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 