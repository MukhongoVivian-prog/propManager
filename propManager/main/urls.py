from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Auth routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Tenant routes
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/bookings/', views.tenant_bookings, name='tenant_bookings'),
    path('tenant/reviews/', views.tenant_reviews, name='tenant_reviews'),
    path('tenant/favorites/', views.tenant_favorites, name='tenant_favorites'),
    path('tenant/settings/', views.tenant_settings, name='tenant_settings'),
]
