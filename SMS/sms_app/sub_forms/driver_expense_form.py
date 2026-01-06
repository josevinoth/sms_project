from django import forms
from ..models import Driverexpense,TripdetailInfo

class DriverExpenseForm(forms.ModelForm):
    class Meta:
        model = Driverexpense
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        settlement = kwargs.pop('settlement', None)
        super().__init__(*args, **kwargs)

        # 🔒 LOCK DRIVER FIELDS
        self.fields['driver_name'].disabled = True
        self.fields['de_driver_id'].disabled = True
        self.fields['trip_number'].required = False

        # ===============================
        # ✅ FILTER TRIP NUMBERS CORRECTLY
        # ===============================
        qs = TripdetailInfo.objects.filter(
            tc_financestatus__id__in=[5, 7, 9]
        )

        if settlement:
            # 🟢 PREFERRED: FILTER BY DRIVER MASTER ID
            if getattr(settlement, 'driver_master_id', None):
                qs = qs.filter(
                    tr_driver_master_id=settlement.driver_master_id
                )
            else:
                # 🟡 FALLBACK: FILTER BY DRIVER NAME
                qs = qs.filter(
                    tr_drivername=settlement.driver
                )

        self.fields['trip_number'].queryset = qs
        self.fields['trip_number'].empty_label = "--Select Trip--"

        self.fields['de_expense_type'].empty_label = "--Select--"

