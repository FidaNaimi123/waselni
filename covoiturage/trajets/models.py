from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator
from login.models import Users  

class Trajet(models.Model):
    # Informations liées au trajet
    point_depart = models.CharField(max_length=100)              # Ville de départ
    point_arrivee = models.CharField(max_length=100)             # Ville d'arrivée
    date_depart = models.DateField()                              # Date de départ
    heure_depart = models.TimeField()                             # Heure de départ
    prix_par_place = models.DecimalField(max_digits=10, decimal_places=2)  # Prix par place
    places_disponibles = models.IntegerField(validators=[MaxValueValidator(limit_value=4, message="le nombre de place doit etre inférieur ou égale à 4")])  
    statut = models.CharField(max_length=20, choices=[
        ('actif', 'Actif'),
        ('complet', 'Complet'),
        ('annulé', 'Annulé')
    ])
    conducteur_nom_complet = models.CharField(max_length=200)     
    conducteur_contact = models.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message="Le contact du conducteur est composé de 8 chiffres."
            )
        ]
    )
    matricule = models.CharField(max_length=20)                   

    # Relation avec le modèle Users dans l'application login
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        return f"{self.point_depart} -> {self.point_arrivee} le {self.date_depart} à {self.heure_depart}"
