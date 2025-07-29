from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),

    # tenant urls
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/bookings/', views.tenant_bookings, name='tenant_bookings'),
    path('tenant/reviews/', views.tenant_reviews, name='tenant_reviews'),
    path('tenant/favorites/', views.tenant_favorites, name='tenant_favorites'),
    path('tenant/settings/', views.tenant_settings, name='tenant_settings'),
    path('properties/', views.properties, name='properties'),
    path('browse/', views.browse_properties, name='browse_properties'),

    # booking flow urls
    path('booking/<int:booking_id>/reserve/', views.reserve_booking, name='reserve_booking'),
    path('booking/<int:booking_id>/checkin/', views.checkin_booking, name='checkin_booking'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:booking_id>/payment/', views.payment_page, name='payment_page'),
    path('booking/<int:booking_id>/process-payment/', views.process_payment, name='process_payment'),
    path('booking/<int:booking_id>/payment-success/', views.payment_success, name='payment_success'),

    # landlord urls
    path('dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('sidebar/',views.sidebar,name = 'landlord_sidebar'),
    path('tenants/', views.tenant_interactions, name='tenant_interactions'),
    path('add-property/', views.add_property, name='add_property'),
    path('settings/', views.landlord_settings, name='landlord_settings'),
    path('landlord/bookings/', views.landlord_bookings, name='landlord_bookings'),
    path('landlord/booking/<int:booking_id>/approve/', views.landlord_approve_booking, name='landlord_approve_booking'),

    # property management
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('property/<int:pk>/delete/', views.delete_property, name='delete_property'),
]