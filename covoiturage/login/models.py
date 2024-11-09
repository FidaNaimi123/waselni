from django.db import models

# Create your models here.
class Users(models.Model):
    email = models.EmailField(max_length=50, unique=True, default='default@gmail.com')
    password = models.CharField(max_length=256)  # Augmenté pour accommoder les mots de passe hachés
    role = models.CharField(max_length=15, default='Utilisateur')
