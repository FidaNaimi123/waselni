from django.db import models
from users.models import Users # Assuming you are linking to the Django User model
from Trip.models import Trajet
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator

class Carpool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(Users, related_name='carpool_groups')
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_carpools', null=True)
    description = models.TextField(blank=True, help_text="Description of the carpool's purpose.")
    rules = models.TextField(blank=True, help_text="Rules for the carpool.")
    creation_date = models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return self.name

class GroupRideReservation(models.Model):
    carpool = models.ForeignKey(Carpool, on_delete=models.CASCADE)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='group_reservations')
    trip = models.ForeignKey(Trajet, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    reservation_deadline = models.DateTimeField(default=timezone.now() + timedelta(hours=1))  # Auto-reject after 1 hour
    members = models.ManyToManyField(Users, through='GroupReservationParticipants')

    def __str__(self):
        return f"Group reservation for {self.carpool.name} on trip {self.trip}"

    def is_expired(self):
        return timezone.now() > self.reservation_deadline


class GroupReservationParticipants(models.Model):
    group_reservation = models.ForeignKey(GroupRideReservation, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('pending', 'Pending')],default='pending')

    def __str__(self):
        return f'{self.user.username} - {self.status}'

class ReservationParticipants(models.Model):
    group_reservation = models.ForeignKey(GroupRideReservation, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('pending', 'Pending')],default='pending')

    def __str__(self):
        return f'{self.user.username} - {self.status}'
    
class GroupReservationNotification(models.Model):
    group_reservation = models.ForeignKey(GroupRideReservation, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='sent')
    notification_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Notification for {self.user.username} - {self.status}'
    
class MembershipInvitation(models.Model):
    carpool = models.ForeignKey(Carpool, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ], default='invited')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invitation for {self.user.username} to {self.carpool.name} - Status: {self.status}'
