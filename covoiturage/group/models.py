from django.db import models
from users.models import Users # Assuming you are linking to the Django User model

class Carpool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(Users, related_name='carpool_groups')
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_carpools', null=True)
    description = models.TextField(blank=True, help_text="Description of the carpool's purpose.")
    rules = models.TextField(blank=True, help_text="Rules for the carpool.")

    def __str__(self):
        return self.name


class GroupRideReservation(models.Model):
    group = models.ForeignKey(Carpool, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    accept_as_group = models.BooleanField(default=True)

    def __str__(self):
        return f'Reservation for {self.group.name} on {self.reservation_date}'


class RideReservationParticipants(models.Model):
    group_ride_reservation = models.ForeignKey(GroupRideReservation, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('pending', 'Pending'),
    ], default='pending')

    def __str__(self):
        return f'{self.user.username} - {self.status}'


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
