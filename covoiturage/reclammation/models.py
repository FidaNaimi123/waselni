from django.db import models
from users.models import Users  # Assuming you are linking to the Django User model
from Trip.models import Trajet

class Reclamation(models.Model):
    utilisateur = models.ForeignKey(Users, on_delete=models.CASCADE)
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reclamations')
    sujet = models.CharField(max_length=255)
    description = models.TextField()
    date_reclamation = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=50, choices=[('en attente', 'En attente'), ('résolue', 'Résolue')], default='en attente')

    def __str__(self):
        return f"Réclamation de {self.utilisateur.email} sur {self.trajet.destination}"
