from django.urls import path
from .views import NotificationListView, notification_add, notification_edit, notification_delete ,RecipientNotificationListView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('liste/', NotificationListView.as_view(), name='notification_list'),
    path('add/', notification_add, name='notification_add'),
    path('edit/<int:pk>/', notification_edit, name='notification_edit'),
    path('delete/<int:pk>/', notification_delete, name='notification_delete'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recipient/', RecipientNotificationListView.as_view(), name='recipient_notifications'),
    
]
