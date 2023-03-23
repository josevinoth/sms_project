from django import forms
from ..models import Packingjobs

class PackingjobsForm(forms.ModelForm):
    class Meta:
        model = Packingjobs
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PackingjobsForm,self).__init__(*args, **kwargs)
        self.fields['bay_branch_name'].empty_label = "--Select--"
        self.fields['Bay_unit_name'].empty_label = "--Select--"