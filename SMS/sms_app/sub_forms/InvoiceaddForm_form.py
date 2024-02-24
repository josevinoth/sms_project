from django import forms
from ..models import BilingInfo,Country,State,City

class InvoiceaddForm(forms.ModelForm):
    class Meta:
        model = BilingInfo
        fields ='__all__'

    def __init__(self, *args, **kwargs):
        super(InvoiceaddForm, self).__init__(*args, **kwargs)
        self.fields['bill_customer_name'].empty_label = "--Select--"
        self.fields['bill_sale_person'].empty_label = "--Select--"
        self.fields['bill_status'].empty_label = "--Select--"
