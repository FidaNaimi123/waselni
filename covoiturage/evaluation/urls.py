from django.urls import path
from .views import create_evaluation, update_evaluation, delete_evaluation

urlpatterns = [
    path('create/<int:trajet_id>/', create_evaluation, name='create_evaluation'),
    path('update/<int:evaluation_id>/', update_evaluation, name='update_evaluation'),
    path('delete/<int:evaluation_id>/', delete_evaluation, name='delete_evaluation'),
]
