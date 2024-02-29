from django import forms
from ..models import iuo_info

class IouForm(forms.ModelForm):
    class Meta:
        model = iuo_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(IouForm,self).__init__(*args, **kwargs)
        self.fields['staff_name'].empty_label = "--Select--"
        self.fields['transaction_type'].empty_label = "--Select--"
        self.fields['business_type'].empty_label = "--Select--"