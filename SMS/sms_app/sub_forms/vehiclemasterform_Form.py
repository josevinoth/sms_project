from django import forms
from ..models import VehiclemasterInfo

class VehiclemasteraddForm(forms.ModelForm):

    class Meta:
        model = VehiclemasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VehiclemasteraddForm,self).__init__(*args, **kwargs)
        self.fields['vm_vehiclemanufacturer'].empty_label = "--Select--"
        self.fields['vm_vehiclemodel'].empty_label = "--Select--"
        self.fields['vm_ownership'].empty_label = "--Select--"
        self.fields['vm_body'].empty_label = "--Select--"
        self.fields['vm_vehicletype'].empty_label = "--Select--"
        self.fields['vm_axletype'].empty_label = "--Select--"
        self.fields['vm_fueltype'].empty_label = "--Select--"
        self.fields['vm_vehiclecolour'].empty_label = "--Select--"
        self.fields['vm_insurancetype'].empty_label = "--Select--"
        self.fields['vm_insurancecopy'].empty_label = "--Select--"
        self.fields['vm_fccopy'].empty_label = "--Select--"
        self.fields['vm_roadtaxcopy'].empty_label = "--Select--"
        self.fields['vm_permittype'].empty_label = "--Select--"
        self.fields['vm_permitcopy'].empty_label = "--Select--"
        self.fields['vm_pollutioncertificatecopy'].empty_label = "--Select--"

