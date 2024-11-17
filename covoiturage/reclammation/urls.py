from django.urls import path
from .views import ReclamationCreateView, ReclamationUpdateView, ReclamationDeleteView

urlpatterns = [
    path('create/', ReclamationCreateView.as_view(), name='reclamation_create'),
    path('edit/<int:pk>/', ReclamationUpdateView.as_view(), name='reclamation_edit'),
    path('delete/<int:pk>/', ReclamationDeleteView.as_view(), name='reclamation_delete'),
]

