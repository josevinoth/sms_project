from django import forms
from ..models import VehicledetailInfo

class VehicledetailaddForm(forms.ModelForm):

    class Meta:
        model = VehicledetailInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VehicledetailaddForm,self).__init__(*args, **kwargs)
        self.fields['ve_transportbusinesstype'].empty_label = "--Select--"
        self.fields['ve_vehiclesource'].empty_label = "--Select--"
        self.fields['ve_vehicletype'].empty_label = "--Select--"
        self.fields['ve_vehiclenumber'].empty_label = "--Select--"
        self.fields['ve_status'].empty_label = "--Select--"
