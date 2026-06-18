from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "LUser"

urlpatterns = [
    # User Dashboard (Main page)
    path("", views.user_dashboard, name="user_dashboard"),
    path("search_ships/", views.search_ships, name="search_ships"),
    path("ship_routes/<int:ship_id>/",views.view_ship_routes,name="view_ship_routes"),

    # 2️⃣ After selecting a route
    path("send_transportation_request/<int:ship_route_id>/",views.send_transportation_request,name="send_transportation_request"),
    path('view_requests/',views.user_view_requests,name='user_view_requests'),
    path('pay_shipping_fee/<int:request_id>/', views.pay_shipping_fee, name='pay_shipping_fee'),
    path("payment-success/<int:request_id>/",views.payment_success,name="payment_success"),
    path('add-address/', views.user_add_address, name='add_address'),
    path("edit-profile/",views.edit_user_profile,name="edit_user_profile"),
    path("available-routes/", views.view_available_routes, name="view_available_routes"),
    path("completed-orders/", views.completed_orders, name="completed_orders"),
    path("submit-review/<int:request_id>/", views.submit_review, name="submit_review"),


    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)