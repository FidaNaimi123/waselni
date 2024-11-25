from django.contrib import admin
from .models import Penalite
from django.utils.html import format_html


@admin.register(Penalite)
class PenaliteAdmin(admin.ModelAdmin):
    # Affichage des champs dans la liste
    list_display = ('utilisateur', 'type_penalite', 'date_penalite', 'occurrences', 'supprimer_compte')
    
    # Ajouter des filtres pour faciliter la recherche
    list_filter = ('type_penalite', 'date_penalite', 'supprimer_compte')
    
    # Champs sur lesquels effectuer une recherche
    search_fields = ('utilisateur__username', 'description')
    
    # Autoriser la modification de certains champs directement depuis la liste
    list_editable = ('supprimer_compte', 'occurrences')
    
    # Organiser les champs dans le formulaire d'administration
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'type_penalite', 'description')
        }),
        ('Détails', {
            'fields': ('date_penalite', 'occurrences', 'supprimer_compte')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_penalite',)

    # Nombre d'objets affichés par page
    list_per_page = 20

    # Tri par défaut
    ordering = ('-date_penalite',)

    # Méthode pour ajouter de la couleur à l'affichage (optionnel)
    def colored_type_penalite(self, obj):
        if obj.type_penalite == 'harcelement':
            return format_html('<span style="color: red;">{}</span>', obj.get_type_penalite_display())
        return obj.get_type_penalite_display()
    
    colored_type_penalite.short_description = 'Type de Pénalité'
