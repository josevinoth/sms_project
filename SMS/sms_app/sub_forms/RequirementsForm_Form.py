from django import forms
from ..models import RequirementsInfo

class RequirementForm(forms.ModelForm):
    class Meta:
        model = RequirementsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RequirementForm,self).__init__(*args, **kwargs)
        self.fields['req_module'].empty_label = "--Select--"
        self.fields['req_owner'].empty_label = "--Select--"
        self.fields['req_bugimprove'].empty_label = "--Select--"
        self.fields['req_implementedby'].empty_label = "--Select--"
        self.fields['req_status'].empty_label = "--Select--"