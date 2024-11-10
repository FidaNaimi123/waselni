from django.contrib import admin
from django.utils.html import format_html
from .models import Evaluation, Trajet

class NoteFilter(admin.SimpleListFilter):
    title = 'Note'
    parameter_name = 'note'

    def lookups(self, request, model_admin):
        return [(i, f'Note {i}') for i in range(1, 6)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(note=self.value())
        return queryset

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('trajet', 'evaluateur', 'evale', 'note', 'date_evaluation', 'details_link')
    search_fields = ('evaluateur__username', 'evale__username', 'trajet__destination')
    list_filter = ('date_evaluation', NoteFilter)
    ordering = ('-date_evaluation',)
    readonly_fields = ('date_evaluation',)
    fieldsets = (
        ('Détails de l\'évaluation', {
            'fields': ('trajet', 'evaluateur', 'evale')
        }),
        ('Note et Date', {
            'fields': ('note', 'date_evaluation')
        }),
    )
    
    def details_link(self, obj):
        
        return format_html('<a href="/admin/app_name/evaluation/{}/change/">Voir détails</a>', obj.id)
    details_link.short_description = 'Action'

admin.site.register(Evaluation, EvaluationAdmin)
