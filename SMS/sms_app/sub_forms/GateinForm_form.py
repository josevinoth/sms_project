from django import forms
from ..models import Gatein_info

class GateinaddForm(forms.ModelForm):
    class Meta:
        model = Gatein_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GateinaddForm, self).__init__(*args, **kwargs)
        self.fields['gatein_driver'].empty_label = "--Select--"
        self.fields['gatein_status'].empty_label = "--Select--"
        self.fields['gatein_truck_type'].empty_label = "--Select--"