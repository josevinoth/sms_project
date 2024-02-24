from django import forms
from ..models import Packingjobs

class PackingjobsForm(forms.ModelForm):
    class Meta:
        model = Packingjobs
        fields = '__all__'

