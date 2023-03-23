from django import forms
from ..models import Materialstock

class MaterialstockForm(forms.ModelForm):
    class Meta:
        model = Materialstock
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MaterialstockForm,self).__init__(*args, **kwargs)
        self.fields['bay_branch_name'].empty_label = "--Select--"
        self.fields['Bay_unit_name'].empty_label = "--Select--"