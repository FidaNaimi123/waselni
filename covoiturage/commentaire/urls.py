from django.urls import path
from .views import create_commentaire, edit_commentaire, delete_commentaire

urlpatterns = [
    path('create/<int:evaluation_id>/', create_commentaire, name='create_commentaire'),
    path('edit/<int:commentaire_id>/', edit_commentaire, name='edit_commentaire'),
    path('delete/<int:commentaire_id>/', delete_commentaire, name='delete_commentaire'),
    
]
