from django import forms
from ..models import SalesInfo
class SalesinfoaddForm(forms.ModelForm):
    class Meta:
        model = SalesInfo
        fields = '__all__'

    s_not_competitive_remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))
    def __init__(self, *args, **kwargs):
        super(SalesinfoaddForm,self).__init__(*args, **kwargs)
        self.fields['s_customer_name'].empty_label = "--Select--"
        self.fields['s_customer_type'].empty_label = "--Select--"
        self.fields['s_customer_new'].empty_label = "--Select--"
        self.fields['s_industry_type'].empty_label = "--Select--"
        self.fields['s_wh_requirement'].empty_label = "--Select--"
        self.fields['s_trans_requirement'].empty_label = "--Select--"
        self.fields['s_pack_requirement'].empty_label = "--Select--"
        self.fields['s_fac_mgmt_requirement'].empty_label = "--Select--"
        self.fields['s_manpower_requirement'].empty_label = "--Select--"
        self.fields['s_supply_type'].empty_label = "--Select--"
        self.fields['s_location'].empty_label = "--Select--"
        self.fields['s_decision_maker'].empty_label = "--Select--"
        self.fields['s_customer_prospective'].empty_label = "--Select--"
        self.fields['s_bus_won_not'].empty_label = "--Select--"
        self.fields['s_not_reason'].empty_label = "--Select--"
        self.fields['s_kyc'].empty_label = "--Select--"
        self.fields['s_contract'].empty_label = "--Select--"
        self.fields['s_rate_approval'].empty_label = "--Select--"
        self.fields['s_approver_name'].empty_label = "--Select--"
        self.fields['s_status'].empty_label = "--Select--"
        self.fields['s_noreason_cp'].empty_label = "--Select--"
        self.fields['s_not_reason'].empty_label = "--Select--"
        self.fields['s_company'].empty_label = "--Select--"
        self.fields['s_payment_cycle'].empty_label = "--Select--"
        self.fields['s_sow'].empty_label = "--Select--"
        self.fields['s_ops_sop'].empty_label = "--Select--"
        self.fields['s_billing_sop'].empty_label = "--Select--"
        self.fields['s_trans_imp'].empty_label = "--Select--"