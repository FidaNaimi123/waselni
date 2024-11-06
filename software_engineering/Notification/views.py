from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Notification
from django.db.models import Q
from django.core.paginator import Paginator

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification_list.html'  # Ensure the correct template path
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
        return context

def notification_add(request):
    if request.method == 'POST':
        type_notification = request.POST.get('type_notification')
        message = request.POST.get('message')
        status_notification = request.POST.get('status_notification')

        Notification.objects.create(
            user=request.user,
            type_notification=type_notification,
            message=message,
            status_notification=status_notification
        )
        return redirect('notification_list')
    
    return render(request, 'notification_add.html')

def notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if request.method == 'POST':
        notification.type_notification = request.POST.get('type_notification')
        notification.message = request.POST.get('message')
        notification.status_notification = request.POST.get('status_notification')
        notification.save()
        return redirect('notification_list')

    return render(request, 'notification_add.html', {'notification': notification})

def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == 'POST':
        notification.delete()
        return redirect('notification_list')

    return render(request, 'notification_confirm_delete.html', {'notification': notification})
