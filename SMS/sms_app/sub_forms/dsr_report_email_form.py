from django import forms
from ..models import DsrInfo

class dsr_EmailForm(forms.Form):
    class Meta:
        model = DsrInfo
        fields = '__all__'
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient emails'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter email message'}),
        }
