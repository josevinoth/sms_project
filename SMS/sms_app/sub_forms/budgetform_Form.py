from django import forms
from ..models import BudgetInfo

class BudgetForm(forms.ModelForm):
    class Meta:
        model = BudgetInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BudgetForm,self).__init__(*args, **kwargs)
        self.fields['bf_updated_by'].empty_label = "--Select--"
        self.fields['bf_location'].empty_label = "--Select--"
        self.fields['bf_unit_reference'].empty_label = "--Select--"
        self.fields['bf_company'].empty_label = "--Select--"
        self.fields['bf_vehicle_source'].empty_label = "--Select--"

        self.fields['bf_unit_reference'].required = False
        self.fields['bf_vehicle_source'].required = False
        self.fields['bf_unit'].required = False
        self.fields['bf_unit'].choices = [('', '--Select--'), ('M-Dept', 'M-Dept'), ('B-Dept', 'B-Dept')]

    def clean_bf_unit_reference(self):
        unit = self.cleaned_data.get('bf_unit_reference')
        if not unit or unit == '0':
            return None
        return unit

    def clean_bf_vehicle_source(self):
        source = self.cleaned_data.get('bf_vehicle_source')
        if not source or source == '0':
            return None
        return source

    def clean_bf_unit(self):
        unit = self.cleaned_data.get('bf_unit')
        if not unit or unit == '0' or unit == '':
            return None
        return unit

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get('bf_company')
        if company and 'trans' in str(company.bvm_business).lower():
            cleaned_data['bf_unit_reference'] = None
        else:
            cleaned_data['bf_vehicle_source'] = None
            cleaned_data['bf_unit'] = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(instance, 'bf_unit_reference_id') and instance.bf_unit_reference_id == '':
            instance.bf_unit_reference = None
        if hasattr(instance, 'bf_vehicle_source_id') and instance.bf_vehicle_source_id == '':
            instance.bf_vehicle_source = None
        if commit:
            instance.save()
        return instance
