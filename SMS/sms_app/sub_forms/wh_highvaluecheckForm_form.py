from django import forms
from ..models import HighvalueInfo

class HighvalueForm(forms.ModelForm):
    class Meta:
        model = HighvalueInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(HighvalueForm,self).__init__(*args, **kwargs)
        self.fields['hc_tilt_watch_sensor_available'].empty_label = "--Select--"
        self.fields['hc_cctv_coverage'].empty_label = "--Select--"
        self.fields['hc_driver_validation_received'].empty_label = "--Select--"
        self.fields['hc_truck_validation'].empty_label = "--Select--"
        self.fields['hc_shipment_information'].empty_label = "--Select--"
        self.fields['hc_customer_informed'].empty_label = "--Select--"
        self.fields['hc_handling_instruction'].empty_label = "--Select--"
        self.fields['hc_commodity'].empty_label = "--Select--"
        self.fields['hc_location'].empty_label = "--Select--"
        self.fields['hc_unit_reference'].empty_label = "--Select--"
        self.fields['hc_condition_cargo_received'].empty_label = "--Select--"
        self.fields['hc_customer'].empty_label = "--Select--"