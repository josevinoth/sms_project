from django import forms
from ..models import BilingInfo, Country, State, City

class InvoiceaddForm(forms.ModelForm):
    class Meta:
        model = BilingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(InvoiceaddForm, self).__init__(*args, **kwargs)
        self.fields['bill_customer_name'].empty_label = "--Select--"
        self.fields['bill_sale_person'].empty_label = "--Select--"
        self.fields['bill_status'].empty_label = "--Select--"

    def clean_bill_invoice_ref(self):
        invoice_ref = self.cleaned_data.get('bill_invoice_ref')
        if not invoice_ref:
            return invoice_ref
        
        invoice_ref = invoice_ref.strip()
        qs = BilingInfo.objects.filter(bill_invoice_ref__iexact=invoice_ref)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                f"Invoice number '{invoice_ref}' already exists! Duplicates are not allowed."
            )
        return invoice_ref
