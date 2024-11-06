from django.contrib import admin
from django.urls import path, include  # Import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notifications/', include('Notification.urls')),  # Include the notifications app's URLs
]
