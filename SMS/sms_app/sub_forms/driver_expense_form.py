from django import forms
from ..models import Driverexpense

class DriverExpenseForm(forms.ModelForm):
    class Meta:
        model = Driverexpense
        exclude = ['driver_settlement_info']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['de_driver_name'].disabled = True
        self.fields['de_driver_id'].disabled = True
        self.fields['trip_number'].empty_label = "--Select--"

