from django import forms
from django.forms import DateInput, TextInput

from ..models import Pregateintruckinfo, Transporter_name

class PregateintruckForm(forms.ModelForm):
    class Meta:
        model = Pregateintruckinfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PregateintruckForm, self).__init__(*args, **kwargs)

        # Set empty labels for dropdowns
        self.fields['pregatein_number'].empty_label = "--Select--"
        self.fields['pregatein_truck_type'].empty_label = "--Select--"
        self.fields['pregatein_updated_by'].empty_label = "--Select--"
        self.fields['pregatein_otl_check'].empty_label = "--Select--"
        self.fields['pregatein_offload_acceptance'].empty_label = "--Select--"
        self.fields['pregatein_otl_type'].empty_label = "--Select--"
        self.fields['pregatein_job_category'].empty_label = "--Select--"
        self.fields['pregatein_transporter_name'].empty_label = "--Select--"
        self.fields['pregatein_transporter_name'].queryset = Transporter_name.objects.all()
        self.fields['pregatein_commodity'].empty_label = "--Select--"
        self.fields['pregatein_approval_status'].empty_label = "--Select--"

