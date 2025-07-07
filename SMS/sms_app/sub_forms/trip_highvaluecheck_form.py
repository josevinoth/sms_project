from django import forms
from ..models import TripHighvalueInfo

class TripHighvalueForm(forms.ModelForm):
    class Meta:
        model = TripHighvalueInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TripHighvalueForm,self).__init__(*args, **kwargs)
        self.fields['thc_vehicleRC'].empty_label = "--Select--"
        self.fields['thc_vehicle_insurance'].empty_label = "--Select--"
        self.fields['thc_goodspermit'].empty_label = "--Select--"
        self.fields['thc_outside_undercarriage'].empty_label = "--Select--"
        self.fields['thc_inoutside_doors'].empty_label = "--Select--"
        self.fields['thc_rightinnerwall'].empty_label = "--Select--"
        self.fields['thc_leftinnerwall'].empty_label = "--Select--"
        self.fields['thc_frontinnerwall'].empty_label = "--Select--"
        self.fields['thc_roof'].empty_label = "--Select--"
        self.fields['thc_floorinside'].empty_label = "--Select--"
        self.fields['thc_gpsfit'].empty_label = "--Select--"
        self.fields['thc_simtracking'].empty_label = "--Select--"
        self.fields['thc_smartlock'].empty_label = "--Select--"
        self.fields['thc_smartlockbaterry'].empty_label = "--Select--"
        self.fields['thc_bottle_otlseal'].empty_label = "--Select--"
        self.fields['thc_commercialinvoice'].empty_label = "--Select--"
        self.fields['thc_eipl_coc'].empty_label = "--Select--"
        self.fields['thc_consignmentnote'].empty_label = "--Select--"
        self.fields['thc_ewaybill'].empty_label = "--Select--"
        self.fields['thc_approval_status'].empty_label = "--Select--"