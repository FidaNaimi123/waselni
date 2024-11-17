from django.contrib import admin
from .models import Reclamation, Trajet
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
    list_display = ('utilisateur', 'trajet', 'sujet', 'etat', 'date_reclamation', 'action_link')
    search_fields = ('utilisateur__username', 'sujet', 'trajet__destination')
    list_filter = ('etat', 'date_reclamation', ReclamationEtatFilter)
    ordering = ('-date_reclamation',)
    readonly_fields = ('date_reclamation',)
    fieldsets = (
        ('Information de l\'utilisateur', {
            'fields': ('utilisateur', 'trajet')
        }),
        ('Détails de la réclamation', {
            'fields': ('sujet', 'description', 'etat')
        }),
        ('Date', {
            'fields': ('date_reclamation',)
        }),
    )
    
    def action_link(self, obj):
        # Creates a clickable link for quick actions
        return format_html('<a href="/admin/app_name/reclamation/{}/change/">Voir détails</a>', obj.id)
    action_link.short_description = 'Action'

admin.site.register(Reclamation, ReclamationAdmin)
