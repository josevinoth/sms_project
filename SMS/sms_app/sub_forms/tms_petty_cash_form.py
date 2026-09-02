from django import forms
from ..models import TMSPettyCashInfo, MyUser

class TMSPettyCashForm(forms.ModelForm):
    class Meta:
        model = TMSPettyCashInfo
        fields = '__all__'
        exclude = ['tpc_created_on', 'tpc_created_by', 'tpc_updated_at', 'tpc_updated_by', 'tpc_number', 'tpc_remarks']
        widgets = {
            'tpc_transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'tpc_trip_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TMSPettyCashForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm'})
            
        if 'tpc_business' in self.fields:
            self.fields['tpc_business'].queryset = self.fields['tpc_business'].queryset.filter(bvm_business__icontains='Trans')
            
        if 'tpc_category' in self.fields:
            self.fields['tpc_category'].queryset = self.fields['tpc_category'].queryset.filter(exp_category_name__icontains='Cash')

        if 'tpc_to' in self.fields:
            self.fields['tpc_to'].queryset = self.fields['tpc_to'].queryset.filter(drivermasterinfo__isnull=False)
            
        if 'tpc_credit_ledger' in self.fields:
            self.fields['tpc_credit_ledger'].queryset = self.fields['tpc_credit_ledger'].queryset.filter(
                ledger_name__icontains='Trans'
            ).exclude(
                ledger_name__icontains='Admin'
            )
        
        # Add select2 class to some fields
        select2_fields = [
            'tpc_business', 'tpc_branch', 'tpc_category', 'tpc_expense_type',
            'tpc_credit_ledger', 'tpc_to', 'tpc_customer', 'tpc_vehicle_source',
            'tpc_vehicle_number', 'tpc_driver_name', 'tpc_unit'
        ]
        for field in select2_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm select2'})
