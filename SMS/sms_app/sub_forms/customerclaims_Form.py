from django import forms
from ..models import CustomerClaimsInfo

class CustomerClaimsForm(forms.ModelForm):
    class Meta:
        model = CustomerClaimsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerClaimsForm, self).__init__(*args, **kwargs)
        self.fields['cc_branch'].empty_label = "--Select--"
        self.fields['cc_unit'].empty_label = "--Select--"
        self.fields['cc_customer'].empty_label = "--Select--"
        self.fields['cc_customer'].queryset = self.fields['cc_customer'].queryset.filter(cu_name__icontains='(T)')
        self.fields['cc_status'].empty_label = "--Select--"
        self.fields['cc_approval_status'].empty_label = "--Select--"