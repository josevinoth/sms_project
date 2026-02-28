from django import forms
from ..sub_models.market_bill_mod import MarketBillInfo
from ..sub_models.vendor_info_mod import Vendor_info


class MarketBillForm(forms.ModelForm):
    mb_vendor = forms.ModelChoiceField(
        queryset=Vendor_info.objects.all().order_by('vend_name'),
        empty_label="-- Select Vendor --",
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "mb_vendor"})
    )

    mb_bill_no = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Bill No"})
    )

    mb_trip_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_trip_cost"})
    )

    mb_loading_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_loading_cost"})
    )

    mb_unloading_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_unloading_cost"})
    )

    mb_parking_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_parking_cost"})
    )

    mb_halting_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_halting_cost"})
    )

    mb_halting_days = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_halting_days"})
    )

    mb_total_cost = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_total_cost"})
    )

    mb_mail_attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "id": "mb_mail_attachment"})
    )

    mb_selected_trips = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "mb_selected_trips"})
    )

    class Meta:
        model = MarketBillInfo
        fields = [
            'mb_vendor',
            'mb_bill_no',
            'mb_trip_cost',
            'mb_loading_cost',
            'mb_unloading_cost',
            'mb_parking_cost',
            'mb_halting_cost',
            'mb_halting_days',
            'mb_total_cost',
            'mb_selected_trips',
            'mb_mail_attachment',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_mb_trip_cost(self):
        val = self.cleaned_data.get('mb_trip_cost')
        return val if val is not None else 0.0

    def clean_mb_parking_cost(self):
        val = self.cleaned_data.get('mb_parking_cost')
        return val if val is not None else 0.0

    def clean_mb_halting_cost(self):
        val = self.cleaned_data.get('mb_halting_cost')
        return val if val is not None else 0.0

    def clean_mb_total_cost(self):
        val = self.cleaned_data.get('mb_total_cost')
        return val if val is not None else 0.0
