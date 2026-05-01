from django import forms
from ..sub_models.trans_invoice_mod import TransInvoiceInfo

class TransInvoiceForm(forms.ModelForm):
    class Meta:
        model = TransInvoiceInfo

        # ✅ FIELDS USER FILLS
        exclude = (
            'ti_branch',
            'ti_total',
            'ti_consignment',
            'ti_trip',
            'ti_goods',
            'ti_department',
            'is_woh',
        )

        widgets = {
            "ti_inv_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),
            "ti_type_of_rate": forms.Select(attrs={"class": "form-control"}),
            "ti_sow": forms.Select(attrs={"class": "form-control"}),
            "ti_aai_sno": forms.TextInput(attrs={"class": "form-control"}),
            # Readonly charges
            "ti_transportation_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_toll_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_parking_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_loading_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_unloading_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_halting_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_docket_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_weighment_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_handling_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ti_cancellation_charges": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super(TransInvoiceForm, self).__init__(*args, **kwargs)
        if 'ti_customer' in self.fields:
            self.fields['ti_customer'].queryset = self.fields['ti_customer'].queryset.filter(cu_name__icontains='(T)')
            self.fields['ti_customer'].empty_label = "--Select--"

    def clean_ti_inv_no(self):
        inv_no = self.cleaned_data.get("ti_inv_no")
        if not inv_no:
            return inv_no

        # Validate uniqueness only among Master invoices (is_woh=False)
        qs = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no, is_woh=False)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Invoice number already exist"
            )
        return inv_no
