from django import forms
from .models import Trajet
import datetime

class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = [
            'point_depart', 
            'point_arrivee', 
            'date_depart', 
            'heure_depart', 
            'prix_par_place', 
            'places_disponibles', 
            'statut', 
            'conducteur_nom_complet', 
            'conducteur_contact', 
            'matricule'
        ]
        widgets = {
            'heure_depart': forms.TimeInput(attrs={'type': 'time'}),  # Champ de type "time"
            'date_depart': forms.DateInput(attrs={'type': 'date'})     # Champ de type "date"
        }
    
    def clean_date_depart(self):
        date_depart = self.cleaned_data.get('date_depart')
        if date_depart and date_depart < datetime.date.today():
            raise forms.ValidationError("La date de départ doit être égale ou supérieure à la date d'aujourd'hui.")
        return date_depart
