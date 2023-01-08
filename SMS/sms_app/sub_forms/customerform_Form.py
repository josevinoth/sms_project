from django import forms
from ..models import CustomerInfo

class CustomeraddForm(forms.ModelForm):
    cu_paymentcycle = forms.ChoiceField(required=False)
    cu_contactno = forms.CharField(required=False)
    cu_email = forms.CharField(required=False)
    cu_tallyid = forms.CharField(required=False)
    class Meta:
        model = CustomerInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomeraddForm,self).__init__(*args, **kwargs)
        self.fields['cu_paymentcycle'].empty_label = "--Select--"
        self.fields['cu_type'].empty_label = "--Select--"
        self.fields['cu_gstexcepmtion'].empty_label = "--Select--"
        self.fields['cu_gstmodel'].empty_label = "--Select--"
        self.fields['cu_paymenttype'].empty_label = "--Select--"
        self.fields['cu_creditcountfrom'].empty_label = "--Select--"
        self.fields['cu_lastmodifiedby'].empty_label = "--Select--"
        self.fields['cu_businessmodel'].empty_label = "--Select--"