from django import forms
from django.contrib.auth.models import User
from ..models import driver_settlement_info, User_extInfo


class DriverSettlementForm(forms.ModelForm):


    staff_name = forms.ModelChoiceField(
        queryset=User_extInfo.objects.select_related('user').filter(
            emp_designation__des_designation_name__iexact="Driver"
        ),
        empty_label="-- Select Driver Name --",
        label="Driver Name",
        required=False
    )


    staff_id = forms.ModelChoiceField(
        queryset=User.objects.filter(
            user_extinfo__emp_designation__des_designation_name__iexact="Driver"
        ),
        empty_label="-- Select Driver ID --",
        label="Driver ID"
    )


    ds_phonenumber = forms.CharField(
        max_length=10,
        required=False,
        label="Driver Phone No"
    )

    class Meta:
        model = driver_settlement_info
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

