from django import forms
from ..models import CustomerInfo

class dsr_EmailForm(forms.Form):
    class Meta:
        model = CustomerInfo
        fields = ['cu_name']  # Include all fields from the model
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient emails'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter email message'}),
        }