from django.urls import path

from main import views

urlpatterns=[
    path('index/', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
     path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Tenant routes
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/bookings/', views.tenant_bookings, name='tenant_bookings'),
    path('tenant/reviews/', views.tenant_reviews, name='tenant_reviews'),
    path('tenant/favorites/', views.tenant_favorites, name='tenant_favorites'),
    path('tenant/settings/', views.tenant_settings, name='tenant_settings'),
    # path('chat_view/', views.chat_view, name='chat_view'), # Renders the chat interface
    # path('send_message/', views.send_message, name='send_message'),
    path('add_property/', views.add_property, name='add_property'), # Add this line
    path('properties/', views.properties, name='properties'), # List properties
]