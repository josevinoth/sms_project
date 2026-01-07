from django import forms
from django.contrib.auth.models import User
from ..sub_models.driver_master_mod import DrivermasterInfo
from ..models import OwnershipInfo


class DriverMasterForm(forms.ModelForm):
    """
    Driver Master Form
    - Own Vehicle  → Employee based
    - Attached     → Manual driver
    """

    # ✅ Override field to control dropdown label
    dm_user_id = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False
    )

    class Meta:
        model = DrivermasterInfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------------------------------
        # Vehicle Source
        # -------------------------------
        self.fields['dm_vehiclesource'].queryset = OwnershipInfo.objects.filter(id__in=[1, 2])
        self.fields['dm_vehiclesource'].empty_label = "--Select Vehicle Source--"

        # -------------------------------
        # Employee Drivers ONLY
        # -------------------------------
        qs = User.objects.filter(user_extinfo__emp_designation_id=4)

        self.fields['dm_user_id'].queryset = qs
        self.fields['dm_user_id'].empty_label = "--Select Employee--"
        self.fields['dm_user_id'].required = False

        # 🔥 THIS FIXES YOUR ISSUE
        self.fields['dm_user_id'].label_from_instance = self.employee_label

        # -------------------------------
        # Optional fields
        # -------------------------------
        self.fields['dm_name'].required = False
        self.fields['dm_id'].required = False

    # ==================================================
    # ✅ DROPDOWN DISPLAY: Name (ID)
    # ==================================================
    def employee_label(self, user):
        emp_id = user.username
        name = f"{user.first_name} {user.last_name}".strip()
        return f"{name} ({emp_id})" if name else f"Driver ({emp_id})"

    # ==================================================
    # ✅ CLEAN LOGIC
    # ==================================================
    def clean(self):
        cleaned_data = super().clean()

        source = cleaned_data.get('dm_vehiclesource')
        user = cleaned_data.get('dm_user_id')
        name = cleaned_data.get('dm_name')

        # -------------------------------
        # OWN VEHICLE
        # -------------------------------
        if source and source.id == 1:
            if not user:
                raise forms.ValidationError(
                    "Employee driver must be selected for Own Vehicle"
                )

            emp_id = user.username
            driver_name = (
                f"{user.first_name} {user.last_name}".strip()
                or emp_id
            )

            cleaned_data['dm_id'] = emp_id
            cleaned_data['dm_name'] = f"{driver_name} ({emp_id})"

        # -------------------------------
        # ATTACHED VEHICLE
        # -------------------------------
        elif source and source.id == 2:
            if not name:
                raise forms.ValidationError(
                    "Driver name is required for Attached Vehicle"
                )

            cleaned_data['dm_user_id'] = None
            cleaned_data['dm_id'] = self.generate_attached_driver_id()

        return cleaned_data

    # ==================================================
    # ✅ ATTACHED DRIVER ID GENERATOR
    # ==================================================
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
