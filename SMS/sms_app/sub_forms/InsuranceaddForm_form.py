from django import forms
from ..models import Insurance_Info
from django.forms import HiddenInput

class InsuranceaddForm(forms.ModelForm):
    ins_attachment = forms.FileField(required=False)
    class Meta:
        model = Insurance_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(InsuranceaddForm,self).__init__(*args, **kwargs)
        self.fields['ins_type'].empty_label = "--Select--"
        self.fields['ins_vendor'].empty_label = "--Select--"
        self.fields['ins_status'].empty_label = "--Select--"
        self.fields['ins_branch'].empty_label = "--Select--"