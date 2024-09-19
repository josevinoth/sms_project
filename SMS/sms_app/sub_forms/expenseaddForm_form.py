from django import forms
from ..models import ExpenseInfo

class ExpenseaddForm(forms.ModelForm):
    class Meta:
        model = ExpenseInfo
        fields ='__all__'
        widgets = {
            'exp_unit_1': forms.SelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseaddForm, self).__init__(*args, **kwargs)
        self.fields['exp_branch'].empty_label = "--Select--"
        self.fields['exp_unit'].empty_label = "--Select--"
        self.fields['exp_vendor'].empty_label = "--Select--"
        self.fields['exp_expense_type'].empty_label = "--Select--"
        self.fields['exp_uom'].empty_label = "--Select--"
        self.fields['exp_category'].empty_label = "--Select--"
        self.fields['exp_business'].empty_label = "--Select--"

