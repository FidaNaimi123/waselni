from django.contrib import admin
from .models import  Reservation
class ReservationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Reservation, ReservationAdmin)
