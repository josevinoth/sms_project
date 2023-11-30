from django import forms
from ..models import Pregateintruckinfo

class PregateintruckForm(forms.ModelForm):
    class Meta:
        model = Pregateintruckinfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PregateintruckForm,self).__init__(*args, **kwargs)
        self.fields['pregatein_number'].empty_label = "--Select--"
        self.fields['pregatein_truck_type'].empty_label = "--Select--"
        self.fields['pregatein_updated_by'].empty_label = "--Select--"
        self.fields['pregatein_otl_check'].empty_label = "--Select--"
        self.fields['pregatein_offload_acceptance'].empty_label = "--Select--"
        self.fields['pregatein_pouch'].empty_label = "--Select--"
        self.fields['pregatein_pouch_yes'].empty_label = "--Select--"