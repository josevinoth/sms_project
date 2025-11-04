from django import forms
from ..models import driver_settlement_info

class DriverSettlementForm(forms.ModelForm):
    class Meta:
        model = driver_settlement_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DriverSettlementForm, self).__init__(*args, **kwargs)
        self.fields['staff_id'].empty_label = "--Select--"
        self.fields['transaction_type'].empty_label = "--Select--"
        self.fields['business_type'].empty_label = "--Select--"
        self.fields['ds_expense_category'].empty_label = "--Select--"
        self.fields['trip'].empty_label = "--Select--"
