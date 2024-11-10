from django.db import models
from users.models import Users

# Create your models here.
class Comptes(models.Model):
    fullname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)  
    phone = models.CharField(max_length=8)
    password = models.CharField(max_length=128)  # Augmenté pour les mots de passe hachés
    user = models.OneToOneField(Users, on_delete=models.CASCADE)