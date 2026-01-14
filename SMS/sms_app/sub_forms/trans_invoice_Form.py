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
