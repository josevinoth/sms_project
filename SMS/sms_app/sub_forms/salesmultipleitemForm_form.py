from django import forms
from ..models import SalesmultipleitemInfo

class SalesmultipleitemForm(forms.ModelForm):
    class Meta:
        model = SalesmultipleitemInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SalesmultipleitemForm,self).__init__(*args, **kwargs)
        self.fields['sm_Rate_Approval'].empty_label = "--Select--"
        self.fields['sm_sales_num'].empty_label = "--Select--"
        self.fields['sm_quote_status'].empty_label = "--Select--"
        self.fields['sm_enquiry_num'].empty_label = "--Select--"
