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
        self.fields['pregatein_invoice_ref'].required = True

        # OPTIMIZATION: Do not load 33,000 records into the select dropdown
        pregatein_id = None
        if self.instance and self.instance.pk:
            pregatein_id = self.instance.pregatein_number_id
        elif self.data and self.data.get('pregatein_number'):
            pregatein_id = self.data.get('pregatein_number')
        elif self.initial and self.initial.get('pregatein_number'):
            pregatein_id = self.initial.get('pregatein_number')
            
        if pregatein_id:
            self.fields['pregatein_number'].queryset = self.fields['pregatein_number'].queryset.filter(pk=pregatein_id)
        else:
            self.fields['pregatein_number'].queryset = self.fields['pregatein_number'].queryset.none()

