from django.contrib import admin
from .models import Reclamation
from django.utils.html import format_html

class ReclamationEtatFilter(admin.SimpleListFilter):
    title = 'État de la réclamation'
    parameter_name = 'etat'

    def lookups(self, request, model_admin):
        return [
            ('en attente', 'En attente'),
            ('résolue', 'Résolue')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'en attente':
            return queryset.filter(etat='en attente')
        if self.value() == 'résolue':
            return queryset.filter(etat='résolue')
        return queryset


class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'sujet', 'point_depart', 'point_arrive', 
                     'temps', 'matricule_voiture', 'etat', 'date_reclamation', 'action_link')
    search_fields = ('utilisateur__username', 'sujet', 'matricule_voiture', 'lieu')
    list_filter = ('etat', 'date_reclamation', ReclamationEtatFilter)
    ordering = ('-date_reclamation',)
    readonly_fields = ('date_reclamation',)
    fieldsets = (
        ('Informations de l\'utilisateur', {
            'fields': ('utilisateur',)
        }),
        ('Détails de la réclamation', {
            'fields': ('sujet', 'description', 'point_depart', 'point_arrive', 
                        'temps', 'matricule_voiture', 'etat')
        }),
        ('Date', {
            'fields': ('date_reclamation',)
        }),
    )
    
    def action_link(self, obj):
        # Crée un lien cliquable pour les actions rapides
        return format_html('<a href="/admin/reclammation/reclamation/{}/change/">Voir détails</a>', obj.id)
    action_link.short_description = 'Action'

admin.site.register(Reclamation, ReclamationAdmin)
