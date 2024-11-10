from django.contrib import admin
from .models import  Trajet
class TripAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trajet, TripAdmin)