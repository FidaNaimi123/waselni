from django import forms
from .models import Reclamation
from users.models import Users
from django.core.exceptions import ValidationError
from django.utils import timezone

class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['utilisateur', 'sujet', 'description', 'point_depart', 'point_arrive',  'temps', 'matricule_voiture']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'etat': forms.Select(choices=[('en attente', 'En attente'), ('résolue', 'Résolue')]),
            'temps': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReclamationForm, self).__init__(*args, **kwargs)
        
        self.fields['utilisateur'].queryset = Users.objects.all()
        
        if 'utilisateur' in self.fields:
            self.fields['utilisateur'].initial = kwargs.get('initial', {}).get('utilisateur', None)

    def clean(self):
        cleaned_data = super().clean()
        sujet = cleaned_data.get('sujet')
        description = cleaned_data.get('description')
        
        if not sujet or not description:
            raise ValidationError("Le sujet et la description sont obligatoires.")
        
        return cleaned_data

    def clean_sujet(self):
        sujet = self.cleaned_data.get('sujet')
        if len(sujet) < 5:
            raise ValidationError("Le sujet de la réclamation doit comporter au moins 5 caractères.")
        return sujet

    def clean_temps(self):
        temps = self.cleaned_data.get('temps')
        if temps < timezone.now():
            raise ValidationError("Le temps indiqué doit être dans le futur.")
        return temps

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 1000:
            raise ValidationError("La description ne peut pas dépasser 1000 caractères.")
        return description
