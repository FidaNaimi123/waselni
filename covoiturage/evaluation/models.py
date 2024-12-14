from django.db import models
from users.models import Users  # Assuming you are linking to the Django User model
from django.core.exceptions import ValidationError
from django.utils import timezone
from Trip.models import Trajet
def validate_date_evaluation(value):
    if value > timezone.now():
        raise ValidationError('La date de l\'évaluation ne peut pas être dans le futur.')


class Evaluation(models.Model):
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE)
    evaluateur = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='evaluations_donnees',default=1)
    evale = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='evaluations_recues')
    note = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    date_evaluation = models.DateTimeField(auto_now_add=True, validators=[validate_date_evaluation])

    def __str__(self):
        return f"Évaluation de {self.evaluateur} pour {self.evale} (Trajet {self.trajet.id})"
    class Meta:
        indexes = [
            models.Index(fields=['trajet', 'evaluateur', 'evale']),  # Ajoute un index composite pour les trois champs
        ]

