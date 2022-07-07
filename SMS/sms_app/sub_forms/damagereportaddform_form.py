from django import forms
from ..models import DamagereportInfo

class DamagereportaddForm(forms.ModelForm):
    class Meta:
        model = DamagereportInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DamagereportaddForm,self).__init__(*args, **kwargs)
        self.fields['dam_damage_type'].empty_label = "--Select--"