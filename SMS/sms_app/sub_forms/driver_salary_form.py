from django import forms
from ..models import DriverSalaryInfo, DrivermasterInfo

class DriverIDChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.dm_id

class DriverSalaryForm(forms.ModelForm):
    ds_driverid = DriverIDChoiceField(
        queryset=DrivermasterInfo.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_driver'}),
        empty_label="--Select Driver ID--"
    )
    ds_month = forms.DateField(
        input_formats=['%Y-%m', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'})
    )
    
    class Meta:
        model = DriverSalaryInfo
        fields = ['ds_driverid', 'ds_branch', 'ds_driver_name', 'ds_month', 'ds_monthly_salary']
        widgets = {
            'ds_monthly_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'ds_branch': forms.Select(attrs={'class': 'form-control', 'id': 'id_branch'}),
            'ds_driver_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_driver_name', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ds_branch'].required = False
        self.fields['ds_driver_name'].required = False
