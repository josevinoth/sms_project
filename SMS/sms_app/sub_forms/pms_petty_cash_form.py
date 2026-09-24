from django import forms
from ..models import PMSPettyCashInfo, PMSExpenseTypeInfo, MyUser

class PMSPettyCashForm(forms.ModelForm):
    class Meta:
        model = PMSPettyCashInfo
        fields = '__all__'
        exclude = ['ppc_created_on', 'ppc_created_by', 'ppc_updated_at', 'ppc_updated_by', 'ppc_number']
        widgets = {
            'ppc_transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'ppc_remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PMSPettyCashForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm'})

        if 'ppc_business' in self.fields:
            self.fields['ppc_business'].queryset = self.fields['ppc_business'].queryset.filter(
                bvm_business__icontains='Pack'
            )

        if 'ppc_branch' in self.fields:
            self.fields['ppc_branch'].queryset = self.fields['ppc_branch'].queryset.filter(
                loc_name__in=['BVM BLR', 'BVM MAA']
            )

        if 'ppc_category' in self.fields:
            self.fields['ppc_category'].queryset = self.fields['ppc_category'].queryset.filter(
                exp_category_name__icontains='Cash'
            )

        if 'ppc_expense_type' in self.fields:
            self.fields['ppc_expense_type'].queryset = PMSExpenseTypeInfo.objects.filter(pms_exp_type_status=True)

        if 'ppc_credit_ledger' in self.fields:
            self.fields['ppc_credit_ledger'].queryset = self.fields['ppc_credit_ledger'].queryset.filter(
                ledger_name__icontains='PACK'
            ).exclude(
                ledger_name__icontains='Admin'
            )

        if 'ppc_customer' in self.fields:
            self.fields['ppc_customer'].queryset = self.fields['ppc_customer'].queryset.filter(
                cu_name__icontains='(P)'
            )

        # Add select2 class to dropdown fields
        select2_fields = [
            'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
            'ppc_credit_ledger', 'ppc_to', 'ppc_customer',
            'ppc_unit'
        ]
        for field in select2_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm select2'})
