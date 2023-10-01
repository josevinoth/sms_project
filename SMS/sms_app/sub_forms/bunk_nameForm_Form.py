from django import forms
from ..models import Bunkname

class BunknameForm(forms.ModelForm):
    class Meta:
        model = Bunkname
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BunknameForm,self).__init__(*args, **kwargs)
        self.fields['bunk_fuel_vendor'].empty_label = "--Select--"