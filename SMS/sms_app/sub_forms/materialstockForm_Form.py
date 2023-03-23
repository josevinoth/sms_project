from django import forms
from ..models import Materialstock

class MaterialstockForm(forms.ModelForm):
    class Meta:
        model = Materialstock
        fields = '__all__'
