from django.urls import path

from main import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    
]