from django import forms
from ..models import PrimeVehicleAllotmentInfo

class PrimeVehicleAllotmentForm(forms.ModelForm):
    pva_vehicletype_selection_requested = forms.BooleanField(initial=True, required=False)
    pva_vehicletype_selection_placed = forms.BooleanField(required=False)

    class Meta:
        model = PrimeVehicleAllotmentInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PrimeVehicleAllotmentForm, self).__init__(*args, **kwargs)
        self.fields['pva_vehiclesource'].empty_label = "--Select--"
        self.fields['pva_vehicletype_placed'].empty_label = "--Select--"
        self.fields['pva_vehicletype'].empty_label = "--Select--"
        self.fields['pva_vehiclenumber'].empty_label = "--Select--"
        self.fields['pva_vendor'].empty_label = "--Select--"
        self.fields['pva_status'].empty_label = "--Select--"

    #  BUSINESS RULE VALIDATION
    def clean(self):
        cleaned_data = super().clean()

        vehicle_source = cleaned_data.get("pva_vehiclesource")
        driver_name = cleaned_data.get("pva_drivername")

        # OWN (1) or ATTACHED (2) - only check driver_name since driver_id is not a form field
        if vehicle_source and vehicle_source.id in [1, 2]:
            if not driver_name:
                self.add_error('pva_drivername', "Driver Name is required for OWN and ATTACHED vehicles.")
            if not cleaned_data.get("pva_vehiclenumber"):
                self.add_error('pva_vehiclenumber', "Vehicle Number is required for OWN and ATTACHED vehicles.")

        # MARKET (3) - check vendor
        if vehicle_source and vehicle_source.id == 3:
            if not cleaned_data.get("pva_vendor"):
                self.add_error('pva_vendor', "Vendor Name is required for MARKET vehicles.")

        return cleaned_data
