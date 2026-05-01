from django import forms
from ..models import PkToolMaster

class PkToolMasterForm(forms.ModelForm):
    class Meta:
        model = PkToolMaster
        fields = [
            'tm_location', 'tm_name', 'tm_size', 'tm_brand', 'tm_model_no',
            'tm_serial_no', 'tm_purchase_date', 'tm_vendor', 'tm_invoice_no',
            'tm_invoice_amount', 'tm_warranty_expiry', 'tm_status',
            'tm_usage_type', 'tm_bill_attachment', 'tm_image'
        ]
        widgets = {
            'tm_purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tm_warranty_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tm_location': forms.Select(attrs={'class': 'form-control select2'}),
            'tm_vendor': forms.Select(attrs={'class': 'form-control select2'}),
            'tm_status': forms.Select(attrs={'class': 'form-control'}),
            'tm_usage_type': forms.Select(attrs={'class': 'form-control'}),
            'tm_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tool Name'}),
            'tm_size': forms.TextInput(attrs={'class': 'form-control'}),
            'tm_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'tm_model_no': forms.TextInput(attrs={'class': 'form-control'}),
            'tm_serial_no': forms.TextInput(attrs={'class': 'form-control'}),
            'tm_invoice_no': forms.TextInput(attrs={'class': 'form-control'}),
            'tm_invoice_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
