from django import forms
from ..models import DsrInfo

class DsrForm(forms.ModelForm):
    class Meta:
        model = DsrInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DsrForm,self).__init__(*args, **kwargs)
        self.fields['ds_customer'].empty_label = "--Select Customer--"
        self.fields['ds_customer'].required = False