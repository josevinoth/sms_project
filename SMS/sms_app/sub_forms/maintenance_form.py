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

    driver_name = forms.ModelChoiceField(
        queryset=DrivermasterInfo.objects.all().order_by('dm_name'),
        empty_label='-- Select Driver --',
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label='Driver'
    )

    class Meta:
        model = MaintenanceInfo
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Disable approval_status field (read-only in UI)
        if "approval_status" in self.fields:
           # show the current value when editing, or the model default when creating
           try:
               if getattr(self.instance, 'pk', None):
                   # editing existing instance: use its value
                   self.fields["approval_status"].initial = self.instance.approval_status
               else:
                   # new form: use the model field default
                   self.fields["approval_status"].initial = (
                       self._meta.model._meta.get_field('approval_status').default
                   )
           except Exception:
               # fallback to 1 if anything goes wrong
               self.fields["approval_status"].initial = 1

           # keep it disabled (read-only) but ensure the bootstrap class is applied
           self.fields["approval_status"].disabled = True
           self.fields["approval_status"].widget.attrs.update({"class": "form-control"})
