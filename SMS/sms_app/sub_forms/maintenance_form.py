from django import forms
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.driver_master_mod import DrivermasterInfo


class MaintenanceForm(forms.ModelForm):
    registration_no = forms.ModelChoiceField(
        queryset=VehiclemasterInfo.objects.all(),
        to_field_name='vm_registrationnumber',
        empty_label="Select Registration No"
    )

    mi_driver_name = forms.ModelChoiceField(
        queryset=DrivermasterInfo.objects.all().order_by('dm_name'),
        empty_label='-- Select Driver --',
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label='Driver'
    )

    mi_est_delivery = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        required=True
    )

    class Meta:
        model = MaintenanceInfo
        exclude = (
            "mi_vehicle",
            "mi_job_card_creator",
            "mi_job_card_created_on",
            "mi_created_at",
            "mi_updated_at",
            "mi_updated_by",
            "mi_job_card_no",
            "mi_approval_status",  # Exclude from form, handled in view
        )
        widgets = {
            "mi_complaint": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format est_delivery for datetime-local input
        if self.instance and self.instance.pk and self.instance.mi_est_delivery:
            self.initial['mi_est_delivery'] = self.instance.mi_est_delivery.strftime("%Y-%m-%dT%H:%M")

        # Make readonly fields not required (they are populated via JS and may not submit)
        readonly_fields = ['mi_make_model', 'mi_registration_date', 'mi_chassis_no', 'mi_engine_no']
        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

