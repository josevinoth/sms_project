from django import forms
from ..models import Driverexpense,TripdetailInfo

class DriverExpenseForm(forms.ModelForm):
    class Meta:
        model = Driverexpense
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔒 LOCK DRIVER FIELDS
        self.fields['driver_name'].disabled = True
        self.fields['de_driver_id'].disabled = True
        self.fields['trip_number'].required = False
        # ✅ Filter Trip Numbers by finance status
        self.fields['trip_number'].queryset = TripdetailInfo.objects.filter(
            tc_financestatus__id__in=[5, 7, 9]
        )

        self.fields['trip_number'].empty_label = "--Select--"
        self.fields['de_expense_type'].empty_label = "--Select--"

