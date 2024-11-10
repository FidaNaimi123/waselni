from django.db import models
from django.contrib.auth.models import User  # Assuming you are linking to the Django User model
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warn', 'Warning'),
        ('alert', 'Alert'),
        ('Invitation', 'Invitation'),
        ('Accept', 'Accept'),
        ('Decline', 'Decline'),
        ('Application', 'Application'),



        # Add more types as needed
    ]

    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        # Add more statuses as needed
    ]

    id_notification = models.AutoField(primary_key=True)
    type_notification = models.CharField(max_length=50, choices=TYPE_CHOICES)
    message = models.TextField()
    status_notification = models.CharField(max_length=50, choices=STATUS_CHOICES)
    date_sent = models.DateTimeField(auto_now_add=True)  # Auto set date when notification is created
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent')  # Sender
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')  # Recipient
    read = models.BooleanField(default=False)  # New field to track whether the notification has been read

    def __str__(self):
        return f"Notification {self.id_notification} - {self.type_notification}"
