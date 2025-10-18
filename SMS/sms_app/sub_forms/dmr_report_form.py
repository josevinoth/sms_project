from django import forms
from ..models import DmrInfo

class DmrForm(forms.ModelForm):
    class Meta:
        model = DmrInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DmrForm, self).__init__(*args, **kwargs)
        self.fields['dmr_customer'].empty_label = "--Select Customer--"
