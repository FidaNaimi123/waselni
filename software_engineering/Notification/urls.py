from django.urls import path
from .views import NotificationListView, notification_add, notification_edit, notification_delete

urlpatterns = [
    path('liste/', NotificationListView.as_view(), name='notification_list'),
    path('add/', notification_add, name='notification_add'),
    path('edit/<int:pk>/', notification_edit, name='notification_edit'),
    path('delete/<int:pk>/', notification_delete, name='notification_delete'),
]
