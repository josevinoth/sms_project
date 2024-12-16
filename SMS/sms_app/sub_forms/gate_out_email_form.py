from django import forms
from ..models import DsrInfo

class gate_out_Form(forms.ModelForm):
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient emails'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter email message'}),
        }