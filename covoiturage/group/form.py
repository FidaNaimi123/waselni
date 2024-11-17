from django import forms
from .models import Carpool

class CarpoolForm(forms.ModelForm):
    class Meta:
        model = Carpool
        fields = ['name', 'description', 'rules'] 