from django import forms
from ..models import Assign_asset_info

class AssignassetaddForm(forms.ModelForm):
    class Meta:
        model = Assign_asset_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AssignassetaddForm, self).__init__(*args, **kwargs)
        self.fields['AA_asset_number'].empty_label = "--Select--"