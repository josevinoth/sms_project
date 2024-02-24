from django import forms
from ..models import WhratemasterInfo

class WhratemasteraddForm(forms.ModelForm):
    class Meta:
        model = WhratemasterInfo
        fields = '__all__'
        # fields = ['whrm_customer_name','whrm_businessmodel','whrm_charge_type','whrm_max_wt','whrm_min_wt','whrm_item','whrm_rate','whrm_total','whrm_description']

    def __init__(self, *args, **kwargs):
        super(WhratemasteraddForm, self).__init__(*args, **kwargs)
        self.fields['whrm_customer_name'].empty_label = "--Select--"
        self.fields['whrm_businessmodel'].empty_label = "--Select--"
        self.fields['whrm_charge_type'].empty_label = "--Select--"
        self.fields['whrm_vehicle_type'].empty_label = "--Select--"