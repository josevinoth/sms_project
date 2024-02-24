from django import forms
from ..models import UnitInfo

class UnitaddForm(forms.ModelForm):
    class Meta:
        model = UnitInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UnitaddForm,self).__init__(*args, **kwargs)
        self.fields['ui_branch_name'].empty_label = "--Select--"