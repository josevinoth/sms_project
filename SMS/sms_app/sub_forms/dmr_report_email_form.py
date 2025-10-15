from django import forms
from ..models import DsrInfo
from ..sub_models.DmrInfo_report import DmrInfo


class dmr_EmailForm(forms.Form):
    class Meta:
        model = DmrInfo
        fields = '__all__'
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient emails'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter email message'}),
        }
