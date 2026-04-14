
from django import forms
from ..sub_models.charge_master_mod import ChargeMasterInfo

class ChargeMasterForm(forms.ModelForm):
    class Meta:
        model = ChargeMasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ChargeMasterForm, self).__init__(*args, **kwargs)
        self.fields['cm_customer'].empty_label = "--Select Customer--"
        self.fields['cm_charge_type'].empty_label = "--Select--"
        self.fields['cm_vehicle_type'].empty_label = "--Select Vehicle Type--"
