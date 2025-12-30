from django import forms
from django.contrib.auth.models import User
from ..sub_models.driver_master_mod import DrivermasterInfo
from ..models import OwnershipInfo


class DriverMasterForm(forms.ModelForm):
    class Meta:
        model = DrivermasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Vehicle source: Own (1), Attached (2)
        self.fields['dm_vehiclesource'].queryset = OwnershipInfo.objects.filter(id__in=[1, 2])
        self.fields['dm_vehiclesource'].empty_label = "--Select Vehicle Source--"

        # Employee drivers only
        self.fields['dm_user_id'].queryset = User.objects.filter(
            user_extinfo__emp_designation_id=4
        )
        self.fields['dm_user_id'].required = False
        self.fields['dm_name'].required = False
        self.fields['dm_id'].required = False

    def clean(self):
        cleaned_data = super().clean()

        source = cleaned_data.get('dm_vehiclesource')
        user = cleaned_data.get('dm_user_id')
        name = cleaned_data.get('dm_name')

        # 🔹 OWN VEHICLE
        if source and source.id == 1:
            if not user:
                raise forms.ValidationError(
                    "Employee driver must be selected for Own Vehicle"
                )

            # ✅ Employee ID VALUE (not numeric DB id)
            cleaned_data['dm_id'] = user.username

            cleaned_data['dm_name'] = (
                    f"{user.first_name} {user.last_name}".strip()
                    or user.username
            )

        # 🔹 ATTACHED VEHICLE
        elif source and source.id == 2:
            if not name:
                raise forms.ValidationError(
                    "Driver name is required for Attached Vehicle"
                )

            cleaned_data['dm_user_id'] = None
            cleaned_data['dm_id'] = self.generate_attached_driver_id()

        return cleaned_data

    def generate_attached_driver_id(self):
        last_driver = (
            DrivermasterInfo.objects
            .filter(dm_id__startswith="ATT-")
            .order_by('-id')
            .first()
        )

        if last_driver and last_driver.dm_id:
            last_no = int(last_driver.dm_id.split('-')[1])
            return f"ATT-{last_no + 1}"

        return "ATT-1001"
