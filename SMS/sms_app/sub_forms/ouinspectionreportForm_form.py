from django import forms
from ..models import Ouinspectreport

class OuinspectreportForm(forms.ModelForm):

    class Meta:
        model = Ouinspectreport
        fields = '__all__'
