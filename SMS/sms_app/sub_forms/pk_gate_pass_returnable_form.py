from django import forms
from ..models import PackingGateReturn

class GatepassreturnForm(forms.ModelForm):
    class Meta:
        model = PackingGateReturn
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GatepassreturnForm,self).__init__(*args, **kwargs)
        self.fields['gp_customer_name'].empty_label = "--Select--"
        self.fields['gp_sales_order_po'].empty_label = "--Select--"
        self.fields['gp_s_name'].empty_label = "--Select--"
        self.fields['gp_uom'].empty_label = "--Select--"
