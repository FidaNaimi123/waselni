from django.db import models
from django.contrib.auth.models import User  # Assuming you are linking to the Django User model

class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warn', 'Warning'),
        ('alert', 'Alert'),
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def creer_notification(self):
        # Logic to create/send notification
        pass

    def modifier_notification(self, **kwargs):
        # Logic to modify the notification
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    def supprimer_notification(self):
        # Logic to delete the notification
        self.delete()

    def __str__(self):
        return f"Notification {self.id_notification} - {self.type_notification}"
