from django.urls import path, include
from . import views

urlpatterns = [
    # home
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),

    # Tenant routes
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/bookings/', views.tenant_bookings, name='tenant_bookings'),
    path('tenant/reviews/', views.tenant_reviews, name='tenant_reviews'),
    path('tenant/favorites/', views.tenant_favorites, name='tenant_favorites'),
    path('tenant/settings/', views.tenant_settings, name='tenant_settings'),
]
