from django import forms
from ..models import CustomerInfo

class CustomeraddForm(forms.ModelForm):

    class Meta:
        model = CustomerInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomeraddForm,self).__init__(*args, **kwargs)
        self.fields['cu_state'].empty_label = "--Select--"
        self.fields['cu_type'].empty_label = "--Select--"
        self.fields['cu_gstexcepmtion'].empty_label = "--Select--"
        self.fields['cu_gstmodel'].empty_label = "--Select--"
        self.fields['cu_paymenttype'].empty_label = "--Select--"
        self.fields['cu_creditcountfrom'].empty_label = "--Select--"
        self.fields['cu_department'].empty_label = "--Select--"
        self.fields['cu_businessmodel'].empty_label = "--Select--"