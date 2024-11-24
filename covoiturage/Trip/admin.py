from django.contrib import admin
from .models import  Trajet

class TripAdmin(admin.ModelAdmin):
    pass
    list_display = (
        'point_depart', 
        'point_arrivee', 
        'date_depart', 
        'heure_depart',  # Ajout de l'heure de départ
        'prix_par_place',  # Ajout du prix par place
        'places_disponibles', 
        'statut', 
        'conducteur_nom_complet', 
        'conducteur_contact',  # Ajout du contact du conducteur
        'matricule'  # Ajout du matricule du véhicule
    )
    search_fields = (
        'point_depart', 
        'point_arrivee', 
        'conducteur_nom_complet', 
        'conducteur_contact'  # Permet de rechercher par contact
    )
    list_filter = (
        'statut', 
        'date_depart', 
        'places_disponibles'  # Ajout d'un filtre pour le nombre de places disponibles
    )
    ordering = ['date_depart', 'heure_depart']  # Sort by date and time of departure by default
    list_per_page = 3  #  pagination
     
    fieldsets = (
    ('Basic Information', {
        'fields': ('point_depart', 'point_arrivee', 'date_depart', 'heure_depart')
    }),
    ('Details', {
        'fields': ('prix_par_place', 'places_disponibles', 'statut')
    }),
    ('Conducteur Information', {
        'fields': ('conducteur_nom_complet', 'conducteur_contact', 'matricule'),
        'classes': ('collapse',)  # Collapsible section
    }),
)
 
    # Action pour annuler les trajets sélectionnés
    def annuler_trajets(self, request, queryset):
        queryset.update(statut='annulé')
    annuler_trajets.short_description = "Annuler les trajets sélectionnés"

    actions = [annuler_trajets]
 
  
admin.site.register(Trajet, TripAdmin)
