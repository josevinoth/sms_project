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

    mb_voucher_no = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly", "placeholder": "Auto-generated"})
    )

    mb_bill_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "id": "mb_bill_date", "required": "required"})
    )

    # Provide a blank "Select" option as the initial value so the dropdown shows a placeholder
    mb_tds_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Select'), ('Company', 'Company'), ('Non company', 'Non company')],
        initial='',
        widget=forms.Select(attrs={"class": "form-control", "id": "mb_tds_type"})
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

    mb_tds_percent = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "mb_tds_percent", "step": "0.01", "min": "0", "max": "100", "placeholder": "0.00"})
    )

    mb_tds_amount = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_tds_amount"})
    )

    mb_payable_amount = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly", "id": "mb_payable_amount"})
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
            'mb_voucher_no',
            'mb_bill_date',
            'mb_tds_type',
            'mb_trip_cost',
            'mb_loading_cost',
            'mb_unloading_cost',
            'mb_parking_cost',
            'mb_halting_cost',
            'mb_halting_days',
            'mb_total_cost',
            'mb_tds_percent',
            'mb_tds_amount',
            'mb_payable_amount',
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

    def clean(self):
        cleaned_data = super().clean()
        bill_no = cleaned_data.get('mb_bill_no')
        selected_trips = cleaned_data.get('mb_selected_trips')

        # 1. Unique check for mb_bill_no
        if bill_no:
            qs = MarketBillInfo.objects.filter(mb_bill_no__iexact=bill_no)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('mb_bill_no', 'A market bill with this Bill No already exists.')

        # 2. Unique check for selected trips (ensure they are not in any other market bill)
        if selected_trips:
            # selected_trips is a comma-separated string, e.g., "18597,18598"
            trip_ids = [tid.strip() for tid in selected_trips.split(',') if tid.strip()]
            for tid in trip_ids:
                # Find other bills containing this trip ID in their mb_selected_trips text
                # We filter and then double-check the split array to prevent partial match issues
                other_bills = MarketBillInfo.objects.filter(mb_selected_trips__icontains=tid)
                if self.instance and self.instance.pk:
                    other_bills = other_bills.exclude(pk=self.instance.pk)
                
                for bill in other_bills:
                    bill_trip_ids = [t.strip() for t in (bill.mb_selected_trips or '').split(',') if t.strip()]
                    if tid in bill_trip_ids:
                        self.add_error(
                            'mb_selected_trips',
                            f"Trip ID {tid} has already been billed in Market Bill '{bill.mb_bill_no}'."
                        )
                        break

        return cleaned_data
