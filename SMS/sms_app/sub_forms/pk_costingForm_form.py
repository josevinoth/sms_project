from django import forms
from ..models import PkcostingInfo

class PkcostingForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkcostingForm,self).__init__(*args, **kwargs)
        self.fields['ct_cost_type'].empty_label = "--Select--"
        self.fields['ct_stock_type'].empty_label = "--Select--"
        self.fields['ct_stock_description'].empty_label = "--Select--"
        self.fields['ct_updated_by'].empty_label = "--Select--"
        self.fields['ct_uom'].empty_label = "--Select--"
        self.fields['ct_assessment_num'].empty_label = "--Select--"
        self.fields['ct_item'].empty_label = "--Select--"
        self.fields['ct_itemdescription'].empty_label = "--Select--"
        self.fields['ct_requirement'].empty_label = "--Select--"
        self.fields['ct_stock_status'].empty_label = "--Select--"
