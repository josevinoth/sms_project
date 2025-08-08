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
        self.fields['pregatein_truck_type'].empty_label = "Select Truck Type"
        self.fields['pregatein_updated_by'].empty_label = "Select Updated By"
        self.fields['pregatein_otl_check'].empty_label = "Select OTL Check"
        self.fields['pregatein_offload_acceptance'].empty_label = "Select Offload Acceptance"
        self.fields['pregatein_otl_type'].empty_label = "Select OTL Type"
        self.fields['pregatein_job_category'].empty_label = "Select Job Category"
        self.fields['pregatein_transporter_name'].empty_label = "Select Transporter Name"
        self.fields['pregatein_transporter_name'].queryset = Transporter_name.objects.all()

        self.fields['pregatein_arrival_date_time'].widget = TextInput(
            attrs={
                'class': 'form-control datetimepicker',
                'id': 'id_pregatein_arrival_date_time',
                'placeholder': 'Select date and time',
                'autocomplete': 'off',
            }
        )
        self.fields['pregatein_dl_exp_date'].widget = DateInput(
            attrs={'class': 'datepicker', 'autocomplete': 'off', 'placeholder': 'Driver DL Expiry Date'}
        )
        self.fields['pregatein_dock_in_date_time'].widget = DateInput(
            attrs={'class': 'datepicker', 'autocomplete': 'off', 'placeholder': 'Dock-In Date & Time'}
        )

        # Add placeholders for text/date/datetime fields
        placeholders = {
            'pregatein_truck_number': 'Truck Number',
            'pregatein_driver': 'Driver Name',
            'pregatein_contact_number': 'Driver Number',
            'pregatein_dl_number': 'Driver DL Number',
            'pregatein_dl_exp_date': 'DL Expiry Date',
            'pregatein_qty': 'Qty',

            'pregatein_otl': 'OTL Number',
        }

        for field, text in placeholders.items():
            self.fields[field].widget.attrs.update({'placeholder': text})
