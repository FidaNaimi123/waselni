from django.urls import path
from .views import creer_trajet, liste_trajets, modifier_trajet, supprimer_trajet,afficher_carte  # Importez les nouvelles vues
from Trip import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('creer_trajet/', creer_trajet, name='creer_trajet'),
    path('liste_trajets/', liste_trajets, name='liste_trajets'),
    path('modifier_trajet/<int:trajet_id>/', modifier_trajet, name='modifier_trajet'),  # URL pour modifier un trajet
    path('supprimer_trajet/<int:trajet_id>/', supprimer_trajet, name='supprimer_trajet'),  # URL pour supprimer un trajet
    path('trajets_disponibles/', views.trajets_disponibles, name='trajets_disponibles'),  # URL pour les trajets disponibles
   path('carte/', afficher_carte, name='afficher_carte'),
   path('statistiques/', views.statistiques_view, name='statistiques'),
   path('export_trajets/', views.export_trajets, name='export_trajets'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)





