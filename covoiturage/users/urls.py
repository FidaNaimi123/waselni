
# login/urls.py
from django.urls import path
from . import views

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
