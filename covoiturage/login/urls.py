"""
URL configuration for covoiturage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from login import views

from django.shortcuts import redirect





urlpatterns = [
    
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('connect/', views.connect, name='connect'),
    path('update_password/', views.update_password, name='update_password'),
    path('liste_users/', views.liste_users, name='liste_users'),
    path('supprimer_utilisateur/<int:id_utilisateur>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('continuer/', views.continuer, name='continuer'),
    path('disconnect/', views.disconnect, name='disconnect'),
]

