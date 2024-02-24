from django import forms
from ..models import BayInfo

class BayaddForm(forms.ModelForm):
    class Meta:
        model = BayInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BayaddForm,self).__init__(*args, **kwargs)
        self.fields['bay_branch_name'].empty_label = "--Select--"
        self.fields['Bay_unit_name'].empty_label = "--Select--"