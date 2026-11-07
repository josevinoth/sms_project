from django import forms
from ..models import Vendor_info

class VendoraddForm(forms.ModelForm):
    class Meta:
        model = Vendor_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VendoraddForm, self).__init__(*args, **kwargs)
        self.fields['vend_branch'].empty_label = "--Select--"
        self.fields['vend_service_type'].empty_label = "--Select--"
        self.fields['vend_status'].empty_label = "--Select--"
        self.fields['vend_description'].empty_label = "--Select--"

        optional_fields = [
            'vend_updated_by',
            'vend_attachment',
            'vend_pan_attachment',
            'vend_gst_attachment',
            'vend_kyc_attachment',
            'vend_bank_attachment',
        ]
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_vend_name(self):
        vend_name = self.cleaned_data.get('vend_name')
        if vend_name:
            vend_name = " ".join(vend_name.strip().split()).upper()
        return vend_name
