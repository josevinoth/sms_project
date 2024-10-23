from django import forms
from ..models import PkstockpurchasesInfo

class PkstockpurchasesForm(forms.ModelForm):

    class Meta:
        model = PkstockpurchasesInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkstockpurchasesForm,self).__init__(*args, **kwargs)
        self.fields['sp_category'].empty_label = "--Select--"
        self.fields['sp_source'].empty_label = "--Select--"
        self.fields['sp_updated_by'].empty_label = "--Select--"
        self.fields['sp_stock_description'].empty_label = "--Select--"
        self.fields['sp_uom'].empty_label = "--Select--"
        self.fields['sp_stock_type'].empty_label = "--Select--"
        self.fields['sp_status'].empty_label = "--Select--"
