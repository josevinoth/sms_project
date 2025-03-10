from django import forms
from ..models import gateinpre_mblInfo

class gateinpre_mblForm(forms.ModelForm):
    class Meta:
        model = gateinpre_mblInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(gateinpre_mblForm,self).__init__(*args, **kwargs)
        self.fields['gpm_branch'].empty_label = "--Select--"
        self.fields['gpm_status'].empty_label = "--Select--"

