from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'type_notification', 'message', 'status_notification', 'date_sent' )
    list_filter = ('status_notification', 'type_notification')
    search_fields = ('user__username', 'message')

    # Method to display the username in the admin interface
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Users Name'
admin.site.register(Notification,NotificationAdmin)
