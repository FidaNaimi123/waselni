from django.db import models
from users.models import Users  # Assuming you are linking to a custom User model
from Trip.models import Trajet
from django.utils import timezone

class Reclamation(models.Model):
    # User making the complaint
    utilisateur = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='reclamations',
        verbose_name="Utilisateur"
    )

    # Subject of the complaint
    sujet = models.CharField(
        max_length=255,
        verbose_name="Sujet"
    )

    # Detailed description of the complaint
    description = models.TextField(
        verbose_name="Description"
    )

    # New fields for trip information
    point_depart = models.CharField(
        max_length=255,
        verbose_name="Point de Départ",
        default="Unknown"
    )
    point_arrive = models.CharField(
        max_length=255,
        verbose_name="Point d'Arrivée",
        default="Unknown"
    )
    
    temps = models.DateTimeField(
        verbose_name="Temps du Trajet",
        default=timezone.now
    )
    matricule_voiture = models.CharField(
        max_length=50,
        verbose_name="Matricule de la Voiture",
        default="0000000"
    )

    # Status of the claim
    etat = models.CharField(
        max_length=50,
        choices=[
            ('en attente', 'En attente'),
            ('résolue', 'Résolue')
        ],
        default='en attente',
        verbose_name="État"
    )

    # Date when the complaint was created
    date_reclamation = models.DateTimeField(
        auto_now_add=True,  # Automatically set to the current date and time when the object is created
        verbose_name="Date de Réclamation"
    )

    def __str__(self):
        # A user-friendly string representation of the object
        return f"Réclamation de {self.utilisateur.email} : {self.sujet} ({self.point_depart} -> {self.point_arrive})"

    class Meta:
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
        ordering = ['-date_reclamation']  # Most recent claims appear first
