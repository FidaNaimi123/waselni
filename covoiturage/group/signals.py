# group/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from Notification.models import Notification  # Corrected import statement
from .models import MembershipInvitation

@receiver(post_save, sender=MembershipInvitation)
def create_notification_for_invitation(sender, instance, created, **kwargs):
    if created:
        # Create a notification when a MembershipInvitation is created
        Notification.objects.create(
            type_notification='Invitation',  # Set type to 'Invitation'
            message=f"This is an invitation to join {instance.carpool.name}.",  # Customize the message
            status_notification='pending',  # You can set this to 'pending' or another status
            date_sent=timezone.now(),  # Set the current time
            user=instance.carpool.creator,  # The logged-in user (creator of the carpool)
            recipient=instance.user,  # The invited user (recipient)
            read=False,  # Mark as unread
        )
