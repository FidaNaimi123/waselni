from django.urls import path
from .views import create_evaluation, update_evaluation, delete_evaluation,select_trip1 , confirmation_view

urlpatterns = [
    path('create/<int:trajet_id>/', create_evaluation, name='create_evaluation'),
    path('select_trip/', select_trip1, name='select_trip1'),
    path('update/<int:evaluation_id>/', update_evaluation, name='update_evaluation'),
    path('delete/<int:evaluation_id>/', delete_evaluation, name='delete_evaluation'),
    
    path('trajets/confirmation/', confirmation_view, name='trajets_disponibles'),  # Nouvelle route

]
