from django import forms
from ..models import PkretrivalInfo

class PkretrivalForm(forms.ModelForm):

    class Meta:
        model = PkretrivalInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkretrivalForm,self).__init__(*args, **kwargs)
        self.fields['pret_cost_type'].empty_label = "--Select--"
        self.fields['pret_stock_type'].empty_label = "--Select--"
        self.fields['pret_stock_description'].empty_label = "--Select--"
        self.fields['pret_updated_by'].empty_label = "--Select--"
        self.fields['pret_uom'].empty_label = "--Select--"
        self.fields['pret_assessment_num'].empty_label = "--Select--"
