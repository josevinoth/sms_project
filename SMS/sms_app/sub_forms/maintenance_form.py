from django import forms
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo


class MaintenanceForm(forms.ModelForm):
    registration_no = forms.ModelChoiceField(
        queryset=VehiclemasterInfo.objects.all(),
        to_field_name='vm_registrationnumber',
        empty_label="Select Registration No"
    )

    class Meta:
        model = MaintenanceInfo

        # ❌ EXCLUDE AUTO-FILLED FIELDS
        exclude = (
            "vehicle",
            "job_card_creator",
            "job_card_created_on",
            "created_at",
            "updated_at",
            "bay_no",
            "job_card_no",
        )