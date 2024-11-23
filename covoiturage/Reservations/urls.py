from django.urls import path
from .views import home,create_reservation,check_user,delete_reservation,update_reservation,select_trip,user_reservations,afficher_historique,test_email

urlpatterns = [
    path('', home, name='home'),  # Route pour la page d'accueil
    path('select_trip/', select_trip, name='select_trip'),  # URL pour traiter la sélection
    #path('reservation/', list_trips, name='list_trips'),  # Route pour réserver un trajet
    path('create_reservation/<int:trip_id>/', create_reservation, name='create_reservation'),  # Créer une réservation
    path('check_user/', check_user, name='check_user'), 
    path('delete_reservation/<int:reservation_id>/', delete_reservation, name='delete_reservation'), 
    path('update_reservation/<int:reservation_id>/', update_reservation, name='update_reservation'), 
    path('user/reservations/', user_reservations, name='user_reservations'),
    path('user/reservations/historique', afficher_historique, name='historique_reservations'),
      path('test-email/', test_email, name='test_email'),

    
]
