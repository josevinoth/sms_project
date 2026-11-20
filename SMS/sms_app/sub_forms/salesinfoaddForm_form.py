from django import forms
from ..models import SalesInfo, NewCustomerMaster
class SalesinfoaddForm(forms.ModelForm):
    class Meta:
        model = SalesInfo
        fields = '__all__'

    s_not_competitive_remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))
    s_customer_new_name = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-modern disable_a_href',
            'id': 's_customer_new_name'
        })
    )

    def __init__(self, *args, **kwargs):
        super(SalesinfoaddForm,self).__init__(*args, **kwargs)
        if not self.instance.pk:  # Only set the default for new instances
            self.fields['s_not_competitive_remarks'].initial = "NA"

        # Populate s_customer_new_name choices from NewCustomerMaster
        new_cust_choices = [('', '--Select New Customer--')]
        try:
            active_new_customers = NewCustomerMaster.objects.filter(is_active=True).order_by('customer_name')
            for c in active_new_customers:
                new_cust_choices.append((c.customer_name, c.customer_name))
        except Exception:
            pass

        if self.instance and self.instance.pk and self.instance.s_customer_new_name:
            curr_val = self.instance.s_customer_new_name
            if curr_val and curr_val not in [c[0] for c in new_cust_choices]:
                new_cust_choices.append((curr_val, curr_val))
            self.fields['s_customer_new_name'].initial = curr_val
        else:
            self.fields['s_customer_new_name'].initial = ""

        self.fields['s_customer_new_name'].widget.choices = new_cust_choices

        self.fields['s_customer_name'].empty_label = "--Select--"
        self.fields['s_customer_type'].empty_label = "--Select--"
        # self.fields['s_customer_new'].empty_label = "--Select--"
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
        self.fields['s_status'].empty_label = "--Select--"
        self.fields['s_noreason_cp'].empty_label = "--Select--"
        self.fields['s_not_reason'].empty_label = "--Select--"
        self.fields['s_company'].empty_label = "--Select--"
        self.fields['s_payment_cycle'].empty_label = "--Select--"
        self.fields['s_sow'].empty_label = "--Select--"
        self.fields['s_ops_sop'].empty_label = "--Select--"
        self.fields['s_billing_sop'].empty_label = "--Select--"
        self.fields['s_trans_imp'].empty_label = "--Select--"
        self.fields['s_express_requirement'].empty_label = "--Select--"
        self.fields['s_tt_requirement'].empty_label = "--Select--"