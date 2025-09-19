from django import forms
from ..models import ExpenseExtinfo

class ExpenseextaddForm(forms.ModelForm):
    class Meta:
        model = ExpenseExtinfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExpenseextaddForm, self).__init__(*args, **kwargs)
        self.fields['exp_ext_expense_number'].empty_label = "--Select--"
        self.fields['exp_ext_branch'].empty_label = "--Select--"
        self.fields['exp_ext_unit'].empty_label = "--Select--"
        self.fields['exp_ext_customer_name'].empty_label = "--Select--"
        self.fields['exp_ext_businessmodel'].empty_label = "--Select--"