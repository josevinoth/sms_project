from django import forms
from ..models import Vendor_info

class VendoraddForm(forms.ModelForm):
    class Meta:
        model = Vendor_info
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(VendoraddForm,self).__init__(*args, **kwargs)
        self.fields['vend_branch'].empty_label = "--Select--"
        self.fields['vend_service_type'].empty_label = "--Select--"
        self.fields['vend_status'].empty_label = "--Select--"