from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.views.generic import ListView
from .models import Notification
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages  # Import messages framework
from users.models import Users # Assuming you are linking to the Django Users model

from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.utils import timezone
from datetime import datetime

from datetime import timedelta
from Reservations.models import Reservation
class RecipientNotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'Notification/recipient_notification_list.html'  # Ensure the correct template path
    context_object_name = 'notifications1'
    paginate_by = 10  # Number of notifications per page

    def get_queryset(self):
        # Retrieve notifications where the recipient is the currently logged-in user
        queryset = Notification.objects.filter(recipient=self.request.user).order_by('-date_sent')

        # Apply filtering by status if provided
        status_filter = self.request.GET.get('status_filter')
        if status_filter:
            queryset = queryset.filter(status_notification=status_filter)

        # Apply filtering by type if provided
        type_filter = self.request.GET.get('type_filter')
        if type_filter:
            queryset = queryset.filter(type_notification=type_filter)

        # Apply search by message if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(Q(message__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status_filter', '')
        context['type_filter'] = self.request.GET.get('type_filter', '')

        # Check if there are any unread notifications for the logged-in user
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            read=False
        )
        invite_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Invitation",
            read=False
        )
        accept_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Accept",
            read=False
        )
        decline_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Decline",
            read=False
        )
        application_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Application",
            read=False
        )

        if decline_notification.exists():
            senders_decline = decline_notification.values_list('user__email', flat=True).distinct()
            senders_dec_list = ', '.join(senders_decline)
            messages.success(self.request, f"{senders_dec_list} declined your invitation.")

        if application_notification.exists():
            senders_app = accept_notification.values_list('user__email', flat=True).distinct()
            senders_app_list = ', '.join(senders_app)
            messages.success(self.request, f"{senders_app_list} requested to join your carpool.")

        if accept_notification.exists():
            senders_accept = accept_notification.values_list('user__email', flat=True).distinct()
            senders_accept_list = ', '.join(senders_accept)
            messages.success(self.request, f"{senders_accept_list} accepted your invitation.")

        if invite_notification.exists():
            senders_invitation = invite_notification.values_list('user__email', flat=True).distinct()
            senders_invitation_list = ', '.join(senders_invitation)
            messages.success(self.request, f"{senders_invitation_list} invited you to join their carpool.")

        if unread_notifications.exists():
            senders = unread_notifications.values_list('user__email', flat=True).distinct()
            senders_list = ', '.join(senders)
            messages.success(self.request, f"You have {unread_notifications.count()} new notification(s) from {senders_list}.")
            unread_notifications.update(read=True)

        
        return context







class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'Notification/notification_list.html'  # Ensure the correct template path
    context_object_name = 'notifications'
    paginate_by = 10  # Number of notifications per page

    def get_queryset(self):
        # Retrieve notifications for the currently logged-in user
        queryset = Notification.objects.filter(user=self.request.user).order_by('-date_sent')
        
        # Apply filtering by status if provided
        status_filter = self.request.GET.get('status_filter')
        if status_filter:
            queryset = queryset.filter(status_notification=status_filter)

        # Apply filtering by type if provided
        type_filter = self.request.GET.get('type_filter')
        if type_filter:
            queryset = queryset.filter(type_notification=type_filter)

        # Apply search by message if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(Q(message__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status_filter', '')
        context['type_filter'] = self.request.GET.get('type_filter', '')

        # Check if there are any unread notifications for the logged-in user
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            read=False
        )
        invite_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Invitation",
            read=False
        )
        accept_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Accept",
            read=False
        )
        decline_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Decline",
            read=False
        )
        Application_notification = Notification.objects.filter(
            recipient=self.request.user,
            type_notification="Application",
            read=False
        )
        if decline_notification.exists():
            senders_decline = decline_notification.values_list('user__email', flat=True).distinct()
            # Join the emails into a comma-separated string
            senders_dec_list = ', '.join(senders_decline)
            messages.success(self.request, f"{senders_dec_list} declined your invitation.")

        if Application_notification.exists():
            senders_app = accept_notification.values_list('user__email', flat=True).distinct()
            # Join the emails into a comma-separated string
            senders_app_list = ', '.join(senders_app)
            messages.success(self.request, f"{senders_app_list} requested to join your carpool")

        if accept_notification.exists():
            senders_accept = accept_notification.values_list('user__email', flat=True).distinct()
            # Join the emails into a comma-separated string
            senders_accept_list = ', '.join(senders_accept)
            messages.success(self.request, f"{senders_accept_list} accepted your invitation.")

        if invite_notification.exists():
            senders_invitation = invite_notification.values_list('user__email', flat=True).distinct()
            # Join the emails into a comma-separated string
            senders_invitation_list = ', '.join(senders_invitation)
            messages.success(self.request, f"{senders_invitation_list} invited you to join their carpool.")

        if unread_notifications.exists():
            # Get the senders of the unread notifications
            senders = unread_notifications.values_list('user__email', flat=True).distinct()
            senders_list = ', '.join(senders)  # Join senders' names in a comma-separated list

            # Add a personalized message with sender information
            messages.success(self.request, f"You have {unread_notifications.count()} new notification(s) from {senders_list}.")

            # Mark all unread notifications as read
            unread_notifications.update(read=True)

        return context


@login_required
def notification_add(request):
    if request.method == 'POST':
        type_notification = request.POST.get('type_notification')
        message = request.POST.get('message')
        status_notification = request.POST.get('status_notification')
        recipient = request.POST.get('recipient')  # Get recipient user ID from the form

        try:
            recipient = Users.objects.get(id=recipient)  # Fetch the recipient user instance
        except Users.DoesNotExist:
            messages.error(request, 'Selected recipient does not exist.')
            return redirect('notification_add')

        # Create the notification with read set to False
        Notification.objects.create(
            user=request.user,  # Sender (current logged-in user)
            type_notification=type_notification,
            message=message,
            status_notification=status_notification,
            recipient=recipient,  # Add recipient field
            read=False,  # Set read to False by default
        )

        # Add a success message to be displayed on the next page load
        messages.success(request, 'A new notification has been successfully created.')

        return redirect('notification_list')

    # List of users excluding the current user
    users = Users.objects.exclude(id=request.user.id)
    return render(request, 'Notification/notification_add.html', {'users': users})

@login_required
def notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if request.method == 'POST':
        notification.type_notification = request.POST.get('type_notification')
        notification.message = request.POST.get('message')
        notification.status_notification = request.POST.get('status_notification')
        notification.read = request.POST.get('read')

        recipient = request.POST.get('recipient')
        try:
            recipient = Users.objects.get(id=recipient)
            notification.recipient = recipient  # Update recipient if needed
        except Users.DoesNotExist:
            messages.error(request, 'Selected recipient does not exist.')
            return redirect('notification_edit', pk=pk)

        notification.save()

        # Add a success message after editing
        messages.success(request, 'The notification has been updated successfully.')

        return redirect('notification_list')

    users = Users.objects.exclude(id=request.user.id)  # List of users excluding the current user
    return render(request, 'Notification/notification_add.html', {'notification': notification, 'users': users})
@login_required
def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == 'POST':
        notification.delete()

        # Add a success message after deletion
        messages.success(request, 'The notification has been deleted successfully.')

        return redirect('notification_list')

    return render(request, 'Notification/notification_confirm_delete.html', {'notification': notification})
