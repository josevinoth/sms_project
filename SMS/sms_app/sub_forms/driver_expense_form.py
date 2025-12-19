from django import forms
from ..models import Driverexpense

class DriverExpenseForm(forms.ModelForm):
    class Meta:
        model = Driverexpense
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only works for ChoiceField / ModelChoiceField
        if 'de_expense_type' in self.fields:
            self.fields['de_expense_type'].empty_label = "-- Select --"
