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
from django.urls import path,include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('evaluation/', include('evaluation.urls')),
    path('commentaire/', include('commentaire.urls')),
    path('reclammation/', include('reclammation.urls')),
    path('reservation/', include('Reservations.urls')),  # Routes pour Reservation
    path('trips/', include('Trip.urls')),  # Routes pour Trip
    path('users/', include('users.urls')),  # Routes pour Users
    path('login/', include('users.urls')),  # Remarquez l'URL 'login/'
    path('group/',include('group.urls')),
    path('notifications/', include('Notification.urls')),
    path('home', TemplateView.as_view(template_name='home/home.html'), name='home1'), 
    path('', TemplateView.as_view(template_name='login/index.html'), name='login'),
]
