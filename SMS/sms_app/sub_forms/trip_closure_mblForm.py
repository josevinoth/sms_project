from django import forms
from ..models import Trclosure_mblInfo

class Trclosure_mblForm(forms.ModelForm):
    class Meta:
        model = Trclosure_mblInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(Trclosure_mblForm,self).__init__(*args, **kwargs)
        self.fields['trm_tripnumber'].empty_label = "--Select--"
        self.fields['trm_departedlocation'].empty_label = "--Select--"
        self.fields['trm_reportedlocation'].empty_label = "--Select--"
        self.fields['trm_status'].empty_label = "--Select--"
