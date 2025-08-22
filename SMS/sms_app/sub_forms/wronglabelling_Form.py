from django import forms
from ..models import WrongLabellingInfo

class WrongLabellingForm(forms.ModelForm):
    class Meta:
        model = WrongLabellingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WrongLabellingForm, self).__init__(*args, **kwargs)
        self.fields['wl_branch'].empty_label = "--Select--"
        self.fields['wl_unit'].empty_label = "--Select--"
        self.fields['wl_customer'].empty_label = "--Select--"
        self.fields['wl_cctvfootage_available'].empty_label = "--Select--"
        self.fields['wl_bvm_fault'].empty_label = "--Select--"
        self.fields['wl_crosslabelling_details'].empty_label = "--Select--"
        self.fields['wl_approval_status'].empty_label = "--Select--"