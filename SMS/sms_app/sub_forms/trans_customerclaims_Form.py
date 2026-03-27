from django import forms
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo

class TransCustomerClaimsForm(forms.ModelForm):
    class Meta:
        model = TransCustomerClaimsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TransCustomerClaimsForm, self).__init__(*args, **kwargs)
        self.fields['tcc_cnote'].empty_label = "--Select--"
        self.fields['tcc_mgmt_approval'].empty_label = "--Select--"
        self.fields['tcc_current_status'].empty_label = "--Select--"
