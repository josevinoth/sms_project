from django import forms
from ..models import PkstockvebdorInfo

class PkstockvendorForm(forms.ModelForm):
    class Meta:
        model = PkstockvebdorInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkstockvendorForm,self).__init__(*args, **kwargs)
        self.fields['spv_vendor_name'].empty_label = "--Select--"