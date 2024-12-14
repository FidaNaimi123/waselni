from django.urls import path
from . import views



urlpatterns = [
    path('carpool/', views.carpool_list, name='carpool_list'),
    path('carpool/add/', views.carpool_add, name='carpool_add'),
    path('carpool/<int:pk>/edit/', views.carpool_edit, name='carpool_edit'),
    path('carpool/<int:pk>/delete/', views.carpool_delete, name='carpool_delete'),
    path('carpool/<int:carpool_id>/add_member/', views.add_member, name='add_member'),
    path('carpool/<int:carpool_id>/remove_member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'), 
    path('carpool/<int:carpool_id>/', views.carpool_detail, name='carpool_detail'),
    path('carpool/<int:carpool_id>/invite/', views.invite_member, name='invite_member'),
    path('carpool/<int:carpool_id>/apply/', views.apply_to_join, name='apply_to_join'),
    path('invitation/<int:invitation_id>/<str:response>/', views.respond_to_invitation, name='respond_to_invitation'),
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('reserve_group/<int:trip_id>/', views.create_group_reservation, name='create_group_reservation'),
    path('reservationInvitations/<int:reservation_id>/', views.confirm_group_reservation, name='confirm_group_reservation'),
    path('select_trip2/', views.select_trip2, name='select_trip2'),
    path('reservationInvitations/', views.reservation_invitations, name='reservation_invitations'),

]
