from django import forms
from ..models import driver_settlement_info
from ..sub_models.driver_master_mod import DrivermasterInfo


class DriverSettlementForm(forms.ModelForm):

    # 🔥 Override driver field
    driver = forms.ModelChoiceField(
        queryset=DrivermasterInfo.objects.all(),
        required=True
    )

    class Meta:
        model = driver_settlement_info
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Empty label
        self.fields['driver'].empty_label = "--Select Driver--"

        # 🔥 THIS FIXES DISPLAY
        self.fields['driver'].label_from_instance = self.driver_label

    # ==================================================
    # ✅ DISPLAY: Driver Name (Driver ID)
    # ==================================================
    def driver_label(self, driver):
        name = driver.dm_name or "Driver"
        driver_id = driver.dm_id or ""
        return f"{name} ({driver_id})" if driver_id else name
