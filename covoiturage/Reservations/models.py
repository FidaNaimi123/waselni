from django.db import models
from Trip.models import Trajet
from users.models import Users
from django.core.validators import MinValueValidator

# Create your models here.
class Reservation(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    trip_id = models.ForeignKey(Trajet, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    Baggage=models.BooleanField(default=False) 
    seat_count = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Le nombre minimal de places doit être 1."
    )
    Payment_Method_list = [
        (' online_payment', ' online_payment'),
        ('cash_payment', 'cash_payment'),
       
    ]

    Payment_Method=models.CharField(max_length=20,choices=Payment_Method_list)

    class Meta:
        unique_together = ('user_id', 'trip_id')  # Contrainte unique
    def __str__(self):
        return f"Reservation for trip {self.trip_id} by user {self.user_id}"


    