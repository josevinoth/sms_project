from django import forms
from ..models import Dispatch_info

class DispatchaddForm(forms.ModelForm):
    dispatch_HAWB = forms.CharField(required=False)
    dispatch_MAWB = forms.CharField(required=False)
    class Meta:
        model = Dispatch_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DispatchaddForm, self).__init__(*args, **kwargs)
        self.fields['dispatch_status'].empty_label = "--Select--"
        self.fields['dispatch_truck_type'].empty_label = "--Select--"
        self.fields['dispatch_truck_type_billing'].empty_label = "--Select--"
        self.fields['dispatch_sticker_pasted_bvm'].empty_label = "--Select--"
        self.fields['dispatch_cargo_picked'].empty_label = "--Select--"
        self.fields['dispatch_customer'].empty_label = "--Select--"
