from datetime import datetime

from django import forms
from ..models import CustomerInfo,CustomerdepartmentInfo,Places

class DmrForm(forms.Form):
    dmr_customer = forms.ModelChoiceField(
        queryset=CustomerInfo.objects.filter(cu_business_sol_id__in=[1, 2]),
        required=False,
        label="Customer"
    )

    customer_department = forms.ModelChoiceField(
        queryset=CustomerdepartmentInfo.objects.all(),
        required=False,
        label="Department"
    )

    month = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 13)],
        required=False,
        label="Month"
    )

    year = forms.ChoiceField(
        choices=[(y, y) for y in range(2020, datetime.now().year + 1)],
        required=False,
        label="Year"
    )

    from_location = forms.ModelChoiceField(
        queryset=Places.objects.all(),
        required=False,
        label="From Location"
    )

    to_location = forms.ModelChoiceField(
        queryset=Places.objects.all(),
        required=False,
        label="To Location"
    )