from django import forms
from ..models import Vendor_info

class VendoraddForm(forms.ModelForm):
    class Meta:
        model = Vendor_info
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(VendoraddForm,self).__init__(*args, **kwargs)
        self.fields['vend_country'].empty_label = "--Select--"
        self.fields['vend_state'].empty_label = "--Select--"
        self.fields['vend_city'].empty_label = "--Select--"
        self.fields['vend_status'].empty_label = "--Select--"