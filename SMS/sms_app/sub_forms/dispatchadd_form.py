from django import forms
from ..models import Dispatch_info

class DispatchaddForm(forms.ModelForm):
    class Meta:
        model = Dispatch_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DispatchaddForm, self).__init__(*args, **kwargs)
        self.fields['dispatch_status'].empty_label = "--Select--"
        self.fields['dispatch_truck_type'].empty_label = "--Select--"
        self.fields['dispatch_customer'].empty_label = "--Select--"
        self.fields['dispatch_department'].empty_label = "--Select--"
        self.fields['dispatch_customer_type'].empty_label = "--Select--"
        self.fields['dispatch_sticker_pasted_BVM'].empty_label = "--Select--"
        self.fields['dispatch_cargo_picked'].empty_label = "--Select--"
