from django.db import models

from django.core.exceptions import ValidationError
from evaluation.models import Evaluation

class Commentaire(models.Model):
    
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='commentaires')
    texte = models.TextField(blank=True, null=True)  
    date_commentaire = models.DateTimeField(auto_now_add=True)  
    
    def clean(self):
        if not self.texte:
            raise ValidationError("Le commentaire ne peut pas être vide.")
        if len(self.texte) < 10:
            raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")
        return super().clean()

    def __str__(self):
        return f"Commentaire pour l'évaluation {self.evaluation.id} de {self.evaluation.evaluateur}"

    class Meta:
        ordering = ['date_commentaire']  