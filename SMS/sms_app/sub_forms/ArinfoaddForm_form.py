from django import forms
from ..models import Ar_Info

class ArinfoaddForm(forms.ModelForm):

    class Meta:
        model = Ar_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ArinfoaddForm,self).__init__(*args, **kwargs)
        self.fields['ar_company'].empty_label = "--Select--"
        self.fields['ar_product'].empty_label = "--Select--"
        self.fields['ar_invoice_num'].empty_label = "--Select--"
        self.fields['ar_branch'].empty_label = "--Select--"
        self.fields['ar_customer_name'].empty_label = "--Select--"
        self.fields['ar_customer_dept'].empty_label = "--Select--"
        self.fields['ar_status'].empty_label = "--Select--"
        self.fields['ar_sales_person'].empty_label = "--Select--"
