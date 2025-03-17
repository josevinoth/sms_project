from django import forms
from ..models import  PkpartcodeInfo

class Part_codeForm(forms.ModelForm):
    class Meta:
        model = PkpartcodeInfo
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(Part_codeForm,self).__init__(*args, **kwargs)
        self.fields['pc_stock_type'].empty_label = "--Select--"
        self.fields['pc_stock_description'].empty_label = "--Select--"
        self.fields['pc_uom'].empty_label = "--Select--"