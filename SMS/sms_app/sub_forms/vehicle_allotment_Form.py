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
        self.fields['va_consignmentnumber'].empty_label = "--Select--"
        self.fields['va_vehiclesource'].empty_label = "--Select--"
        self.fields['va_vehicletype_placed'].empty_label = "--Select--"
        self.fields['va_vehicletype'].empty_label = "--Select--"
        self.fields['va_vehiclenumber'].empty_label = "--Select--"