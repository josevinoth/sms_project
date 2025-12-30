from django import forms
from django.contrib.auth.models import User
from ..models import driver_settlement_info, DrivermasterInfo


class DriverSettlementForm(forms.ModelForm):

    driver = forms.ModelChoiceField(
        queryset=DrivermasterInfo.objects.all(),
        empty_label="Select Driver"
    )

    class Meta:
        model = driver_settlement_info
        fields = "__all__"

    class Meta:
        model = driver_settlement_info
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

