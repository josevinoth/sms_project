from django import forms
from ..models import Vehicle_allotmentInfo

class VehicleallotmentForm(forms.ModelForm):
    va_vehicletype_selection_requested = forms.BooleanField(initial=True,required=False)
    va_vehicletype_selection_placed = forms.BooleanField(required=False)
    class Meta:
        model = Vehicle_allotmentInfo
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(VehicleallotmentForm,self).__init__(*args, **kwargs)
        if 'va_vehiclesource' in self.fields:
            self.fields['va_vehiclesource'].empty_label = "--Select--"
        if 'va_vehicletype_placed' in self.fields:
            self.fields['va_vehicletype_placed'].empty_label = "--Select--"
        if 'va_vehicletype' in self.fields:
            self.fields['va_vehicletype'].empty_label = "--Select--"
        if 'va_vehiclenumber' in self.fields:
            self.fields['va_vehiclenumber'].empty_label = "--Select--"
        if 'va_vendor' in self.fields:
            self.fields['va_vendor'].empty_label = "--Select--"
        if 'va_status' in self.fields:
            self.fields['va_status'].empty_label = "--Select--"
        if 'va_updated_by' in self.fields:
            self.fields['va_updated_by'].required = False
        if 'va_created_by' in self.fields:
            self.fields['va_created_by'].required = False
        if 'va_enquirynumber' in self.fields:
            self.fields['va_enquirynumber'].required = False
        if 'va_driver_lic_expiry' in self.fields:
            self.fields['va_driver_lic_expiry'].widget.attrs['readonly'] = 'readonly'
            self.fields['va_driver_lic_expiry'].widget.attrs['style'] = 'pointer-events: none;'

    #  BUSINESS RULE VALIDATION
    def clean(self):
        cleaned_data = super().clean()

        vehicle_source = cleaned_data.get("va_vehiclesource")
        driver_name = cleaned_data.get("va_drivername")

        # OWN (1) or ATTACHED (2) - only check driver_name since driver_id is not a form field
        if vehicle_source and vehicle_source.id in [1, 2]:
            if not driver_name:
                self.add_error('va_drivername', "Driver Name is required for OWN and ATTACHED vehicles.")
            if not cleaned_data.get("va_vehiclenumber"):
                self.add_error('va_vehiclenumber', "Vehicle Number is required for OWN and ATTACHED vehicles.")

        # MARKET (3) - check vendor
        if vehicle_source and vehicle_source.id == 3:
            if not cleaned_data.get("va_vendor"):
                self.add_error('va_vendor', "Vendor Name is required for MARKET vehicles.")

        return cleaned_data
