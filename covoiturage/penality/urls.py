from django.urls import path
from . import views

app_name = 'penalites'


urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/ajouter-penalite/', views.ajouter_penalite, name='ajouter_penalite'),
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),
    path('api/modifier-score/', views.calculer_score, name='modifier_score'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('historique/', views.historique, name='historique'),
]

