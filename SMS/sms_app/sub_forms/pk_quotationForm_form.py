from django import forms
from ..models import PkquotationInfo

class PkquotationForm(forms.ModelForm):

    class Meta:
        model = PkquotationInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkquotationForm,self).__init__(*args, **kwargs)
        self.fields['pkqt_cost_type'].empty_label = "--Select--"
        self.fields['pkqt_stock_type'].empty_label = "--Select--"
        self.fields['pkqt_stock_description'].empty_label = "--Select--"
        self.fields['pkqt_updated_by'].empty_label = "--Select--"
        self.fields['pkqt_uom'].empty_label = "--Select--"
        self.fields['pkqt_assessment_num'].empty_label = "--Select--"
