from django import forms
from ..models import Pregateintruckinfo

class PregateintruckmblForm(forms.ModelForm):
    class Meta:
        model = Pregateintruckinfo
        fields = ['pregatein_job_category', 'pregatein_otl_type', 'pregatein_offload_acceptance',
            'pregatein_otl_check', 'pregatein_updated_by', 'pregatein_number',
            'pregatein_truck_type', 'pregatein_dl_exp_date', 'pregatein_high_value',
            'pregatein_transporter', 'pregatein_driver', 'pregatein_contact_number',
            'pregatein_dl_number', 'pregatein_otl','pregatein_high_value','pregatein_job_category',
            'pregatein_arrival_date_time','pregatein_dock_in_date_time','pregatein_truck_number','pregatein_qty']

    def __init__(self, *args, **kwargs):
        super(PregateintruckmblForm,self).__init__(*args, **kwargs)
        self.fields['pregatein_number'].empty_label = "--Select--"
        self.fields['pregatein_truck_type'].empty_label = "--Select--"
        self.fields['pregatein_updated_by'].empty_label = "--Select--"
        self.fields['pregatein_otl_check'].empty_label = "--Select--"
        self.fields['pregatein_offload_acceptance'].empty_label = "--Select--"
        self.fields['pregatein_otl_type'].empty_label = "--Select--"
        self.fields['pregatein_job_category'].empty_label = "--Select--"