from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # tenant urls
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/bookings/', views.tenant_bookings, name='tenant_bookings'),
    path('tenant/reviews/', views.tenant_reviews, name='tenant_reviews'),
    path('tenant/favorites/', views.tenant_favorites, name='tenant_favorites'),
    path('tenant/settings/', views.tenant_settings, name='tenant_settings'),

    # landlord urls
    path('dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('sidebar/',views.sidebar,name = 'landlord_sidebar'),
    path('tenants/', views.tenant_interactions, name='view_tenants'),
    path('add-property/', views.add_property, name='add_property'),
    path('property/<int:property_id>/', views.view_property, name='view_properties'),
]