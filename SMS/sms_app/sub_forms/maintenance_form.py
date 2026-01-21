from django import forms
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.driver_master_mod import  DrivermasterInfo

class MaintenanceForm(forms.ModelForm):
    registration_no = forms.ModelChoiceField(
        queryset=VehiclemasterInfo.objects.all(),
        to_field_name='vm_registrationnumber',
        empty_label="Select Registration No"
    )

    # Define driver_name as a ModelChoiceField so the form renders a dropdown
    driver_name = forms.ModelChoiceField(
        queryset=DrivermasterInfo.objects.all().order_by('dm_name'),
        empty_label='-- Select Driver --',
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label='Driver'
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
        widgets = {
            "complaint": forms.Select(attrs={"class": "form-control"}),
        }
