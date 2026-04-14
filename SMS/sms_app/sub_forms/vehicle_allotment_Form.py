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
        self.fields['va_vehiclesource'].empty_label = "--Select--"
        self.fields['va_vehicletype_placed'].empty_label = "--Select--"
        self.fields['va_vehicletype'].empty_label = "--Select--"
        self.fields['va_vehiclenumber'].empty_label = "--Select--"
        self.fields['va_vendor'].empty_label = "--Select--"
        self.fields['va_status'].empty_label = "--Select--"

    # 🔥 BUSINESS RULE VALIDATION
    def clean(self):
        cleaned_data = super().clean()

        vehicle_source = cleaned_data.get("va_vehiclesource")
        driver_name = cleaned_data.get("va_drivername")

        # OWN (1) or ATTACHED (2) - only check driver_name since driver_id is not a form field
        if vehicle_source and vehicle_source.id in [1, 2]:
            if not driver_name:
                self.add_error('va_drivername', "Driver Name is required for OWN and ATTACHED vehicles.")

        # MARKET (3) - check vendor
        if vehicle_source and vehicle_source.id == 3:
            if not cleaned_data.get("va_vendor"):
                self.add_error('va_vendor', "Vendor Name is required for MARKET vehicles.")

        return cleaned_data
