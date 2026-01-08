from django import forms
from ..sub_models.trans_invoice_mod import TransInvoiceInfo

class TransInvoiceForm(forms.ModelForm):
    class Meta:
        model = TransInvoiceInfo
        fields = '__all__'

    widgets = {
        "ti_inv_date": forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    }