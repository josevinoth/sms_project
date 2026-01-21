from datetime import datetime
import calendar
from django import forms
from ..models import CustomerInfo, CustomerdepartmentInfo, Places


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
        choices=[(0, '---')] + [(i, calendar.month_name[i][:10]) for i in range(1, 13)],
        required=False,
        label="Month",
        initial=0
    )

    current_year = datetime.now().year
    default_year = 2026

    year = forms.ChoiceField(
        choices=[(0, '---')] + [
            (y, y) for y in range(2020, max(current_year, default_year) + 1)
        ],
        required=False,
        label="Year",
        initial=default_year
    )

    vehicle_number = forms.CharField(
        required=False,
        label="Vehicle Number",
        initial="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Vehicle Number'
        })
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
