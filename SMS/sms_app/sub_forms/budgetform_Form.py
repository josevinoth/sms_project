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
