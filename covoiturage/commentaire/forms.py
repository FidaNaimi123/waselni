from django import forms
from django.core.exceptions import ValidationError
from .models import Commentaire


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['evaluation', 'texte']  
        widgets = {
            'texte': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    
    def clean_texte(self):
        texte = self.cleaned_data.get('texte')

        
        if texte and len(texte) < 10:
            raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")
        
    
        if texte and len(texte) > 500:
            raise ValidationError("Le commentaire ne peut pas dépasser 500 caractères.")
        
        return texte

    # Vérification de l'association avec une Evaluation valide (actif, ou dans un état spécifique)
    def clean_evaluation(self):
        evaluation = self.cleaned_data.get('evaluation')

        # Si l'évaluation est dans un état "résolue" ou "archivée", le commentaire ne peut pas être ajouté
        if evaluation and evaluation.etat == 'résolue':
            raise ValidationError("Vous ne pouvez pas ajouter de commentaire pour une évaluation déjà résolue.")
        
        return evaluation

    
    def clean(self):
        cleaned_data = super().clean()
        evaluation = cleaned_data.get('evaluation')
        utilisateur = self.instance.evaluation.evaluateur if self.instance else None  

        if evaluation and utilisateur != self.user: 
            raise ValidationError("Vous ne pouvez commenter que vos propres évaluations.")
        
        return cleaned_data
