from django import forms
from ..models import WMSPettyCashInfo, WMSExpenseTypeInfo, MyUser

class WMSPettyCashForm(forms.ModelForm):
    class Meta:
        model = WMSPettyCashInfo
        fields = '__all__'
        exclude = ['wpc_created_on', 'wpc_created_by', 'wpc_updated_at', 'wpc_updated_by', 'wpc_number']
        widgets = {
            'wpc_transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'wpc_remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(WMSPettyCashForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm'})

        if 'wpc_business' in self.fields:
            self.fields['wpc_business'].queryset = self.fields['wpc_business'].queryset.filter(
                bvm_business__icontains='Storage'
            )

        if 'wpc_category' in self.fields:
            self.fields['wpc_category'].queryset = self.fields['wpc_category'].queryset.filter(
                exp_category_name__icontains='Cash'
            )

        if 'wpc_expense_type' in self.fields:
            self.fields['wpc_expense_type'].queryset = WMSExpenseTypeInfo.objects.filter(wms_exp_type_status=True)

        if 'wpc_credit_ledger' in self.fields:
            self.fields['wpc_credit_ledger'].queryset = self.fields['wpc_credit_ledger'].queryset.filter(
                ledger_name__icontains='WH'
            ).exclude(
                ledger_name__icontains='Admin'
            )

        # Add select2 class to dropdown fields
        select2_fields = [
            'wpc_business', 'wpc_branch', 'wpc_category', 'wpc_expense_type',
            'wpc_credit_ledger', 'wpc_to', 'wpc_customer', 'wpc_business_model',
            'wpc_unit'
        ]
        for field in select2_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm select2'})
