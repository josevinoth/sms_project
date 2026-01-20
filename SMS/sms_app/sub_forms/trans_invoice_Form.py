from django import forms
from ..sub_models.trans_invoice_mod import TransInvoiceInfo

class TransInvoiceForm(forms.ModelForm):
    class Meta:
        model = TransInvoiceInfo

        # ✅ ONLY fields user fills
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
            )
        }

    # ==================================================
    # 🔒 STEP-2: UNIQUE INVOICE NUMBER VALIDATION
    # ==================================================
    def clean_ti_inv_no(self):
        inv_no = self.cleaned_data.get("ti_inv_no")

        # Allow empty handling if field is optional
        if not inv_no:
            return inv_no

        qs = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no)

        # ✅ Important: allow same invoice number while editing
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Invoice number already exists. Please enter a unique invoice number."
            )

        return inv_no
