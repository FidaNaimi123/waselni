from django.contrib import admin
from .models import Commentaire
from evaluation.models import Evaluation
from django.utils.html import format_html

class CommentaireLengthFilter(admin.SimpleListFilter):
    title = 'Longueur du commentaire'
    parameter_name = 'longueur'

    def lookups(self, request, model_admin):
        return [
            ('short', 'Court (< 50 caractères)'),
            ('medium', 'Moyen (50-100 caractères)'),
            ('long', 'Long (> 100 caractères)')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(texte__length__lt=50)
        elif self.value() == 'medium':
            return queryset.filter(texte__length__gte=50, texte__length__lte=100)
        elif self.value() == 'long':
            return queryset.filter(texte__length__gt=100)
        return queryset

class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'texte_excerpt', 'date_commentaire', 'details_link')
    search_fields = ('evaluation__evaluateur__username', 'texte')
    list_filter = ('date_commentaire', CommentaireLengthFilter)
    ordering = ('-date_commentaire',)
    readonly_fields = ('date_commentaire',)
    fieldsets = (
        ('Détails du commentaire', {
            'fields': ('evaluation', 'texte')
        }),
        ('Date', {
            'fields': ('date_commentaire',)
        }),
    )

    def texte_excerpt(self, obj):
        return (obj.texte[:30] + '...') if len(obj.texte) > 30 else obj.texte
    texte_excerpt.short_description = 'Extrait du texte'

    def details_link(self, obj):
        return format_html('<a href="/admin/app_name/commentaire/{}/change/">Voir détails</a>', obj.id)
    details_link.short_description = 'Action'

admin.site.register(Commentaire, CommentaireAdmin)
