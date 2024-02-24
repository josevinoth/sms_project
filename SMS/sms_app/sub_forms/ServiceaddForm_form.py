from django import forms
from ..models import Service_Info

class ServiceaddForm(forms.ModelForm):
    class Meta:
        model = Service_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ServiceaddForm,self).__init__(*args, **kwargs)
        self.fields['ser_asset'].empty_label = "--Select--"
        self.fields['ser_vendor'].empty_label = "--Select--"
        self.fields['ser_status'].empty_label = "--Select--"