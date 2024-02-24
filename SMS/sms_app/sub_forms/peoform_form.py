from django import forms
from ..models import Peo_reg

class PeoaddForm(forms.ModelForm):
    class Meta:
        model = Peo_reg
        fields = '__all__'
