
# login/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('connect/', views.connect, name='connect'),
    path('connect_remember/', views.connect_remember, name='connect_remember'),
    path('update_password/', views.update_password, name='update_password'),
    path('disconnect/', views.disconnect, name='disconnect'),
]
