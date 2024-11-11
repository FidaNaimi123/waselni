from django import forms
from .models import Evaluation
from django.core.exceptions import ValidationError
from datetime import timedelta

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['note'] 
        widgets = {
            'note': forms.Select(choices=[(i, i) for i in range(1, 6)]),  
            'comments': forms.Textarea(attrs={'placeholder': 'Add your comments (optional)', 'rows': 3}),
        }
    def clean_date_evaluation(self):
        date_evaluation = self.cleaned_data['date_evaluation']
        trajet = self.cleaned_data['trajet']  

        if date_evaluation > (trajet.heure_depart + timedelta(days=30)):
            raise ValidationError(f"L'évaluation doit avoir lieu dans les 30 jours suivant la fin du trajet.")
        
        return date_evaluation
    def clean(self):
        cleaned_data = super().clean()
        evaluateur = cleaned_data.get('evaluateur')
        evale = cleaned_data.get('evale')

       

        return cleaned_data
