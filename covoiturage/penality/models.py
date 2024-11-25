from django.db import models
from users.models import Users

# Create your models here.
class Penalite(models.Model):
    utilisateur = models.ForeignKey(Users, on_delete=models.CASCADE)
    type_penalite = models.CharField(max_length=50, choices=[
        ('annulation_tardive', 'Annulation Tardive'),
        ('harcelement', 'Harcèlement'),
        ('point_descente_faux', 'Point de descente incorrect'),
        ('nombre_places_incorrect', 'Nombre de places incorrect'),
        ('disponibilite_bagages_incorrecte', 'Disponibilité des bagages incorrecte'),
        ('paiement_non_effectue', 'Paiement non effectué'),
        # Ajouter d'autres types si nécessaire
    ])
    description = models.TextField()
    date_penalite = models.DateTimeField(auto_now_add=True)
    supprimer_compte = models.BooleanField(default=False)
    occurrences = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"Pénalité ({self.type_penalite}) pour {self.utilisateur}"
