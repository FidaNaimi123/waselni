from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['Baggage', 'seat_count', 'Payment_Method']  # Retirer 'user_id' des champs
        widgets = {
            'seat_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'Baggage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Payment_Method': forms.Select(attrs={'class': 'form-control'}),
        }