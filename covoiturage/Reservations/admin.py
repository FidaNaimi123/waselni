# admin.py
from django.contrib import admin
from django.http import HttpResponse
from .models import Reservation, Reservation_Historique
from xhtml2pdf import pisa
from django.template.loader import render_to_string

def export_as_pdf(modeladmin, request, queryset):
    # Générer un PDF avec les réservations sélectionnées
    template_path = 'admin/export_pdf.html'
    context = {'reservations': queryset}
    html = render_to_string(template_path, context)
    
    # Créer la réponse HTTP avec le fichier PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reservations.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Si une erreur survient lors de la génération
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)
    return response

export_as_pdf.short_description = "Exporter comme PDF"

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'trip_id', 'reservation_date', 'seat_count', 'Baggage', 'Payment_Method')
    search_fields = ('user_id__username', 'trip_id__nom', 'Payment_Method')
    list_filter = ('Baggage', 'Payment_Method', 'reservation_date')
    list_editable = ('seat_count', 'Baggage', 'Payment_Method')
    ordering = ('-reservation_date',)
    fieldsets = (
        ("Informations générales", {
            'fields': ('user_id', 'trip_id', 'reservation_date')
        }),
        ("Détails de la réservation", {
            'fields': ('seat_count', 'Baggage', 'Payment_Method'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ()

    # Ajouter l'action PDF
    actions = [export_as_pdf]


class Reservation_HistoriqueAdmin(admin.ModelAdmin):
    list_display = ('user', 'trajet', 'date_reservation', 'nombre_places', 'baggage', 'date_annulation')
    search_fields = ('user__username', 'trajet__nom', 'date_reservation')
    list_filter = ('baggage', 'date_reservation', 'date_annulation')
    list_editable = ('nombre_places', 'baggage')
    ordering = ('-date_reservation',)
    fieldsets = (
        ("Informations générales", {
            'fields': ('user', 'trajet', 'date_reservation', 'date_annulation')
        }),
        ("Détails de la réservation", {
            'fields': ('nombre_places', 'baggage'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ()

    # Ajouter l'action PDF
    actions = [export_as_pdf]


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Reservation_Historique, Reservation_HistoriqueAdmin)
