from django import forms
from ..models import Fuelfillinginfo

class FuelfillingForm(forms.ModelForm):

    class Meta:
        model = Fuelfillinginfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FuelfillingForm,self).__init__(*args, **kwargs)
        self.fields['ff_vehicle_num'].empty_label = "--Select--"
        self.fields['ff_bunk_name'].empty_label = "--Select--"
        self.fields['ff_updated_by'].empty_label = "--Select--"
        self.fields['ff_city'].empty_label = "--Select--"
        self.fields['ff_loaction'].empty_label = "--Select--"
