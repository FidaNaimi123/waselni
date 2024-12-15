from django.db import models
from users.models import Users

import os 
from django.conf import settings
# Create your models here.
class Comptes(models.Model):
    fullname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)  
    phone = models.CharField(max_length=8)
    password = models.CharField(max_length=128)  # Augmenté pour les mots de passe hachés
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # Définir l'emplacement


    def save(self, *args, **kwargs):
        # Supprimer l'ancienne image si une nouvelle est téléchargée
        if self.pk:
            old_image = Comptes.objects.filter(pk=self.pk).first().image
            if old_image and old_image != self.image:
                old_image_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
        super().save(*args, **kwargs)



    def __str__(self):
        return self.fullname
