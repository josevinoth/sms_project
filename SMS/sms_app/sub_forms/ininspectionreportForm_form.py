from django import forms
from ..models import Ininspectreport

class IninspectreportForm(forms.ModelForm):

    class Meta:
        model = Ininspectreport
        fields = '__all__'
