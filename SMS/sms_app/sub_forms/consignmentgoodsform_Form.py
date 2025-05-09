from django import forms
from ..models import ConsignmentgoodsInfo,Stock_type


class ConsignmentgoodsaddForm(forms.ModelForm):

    class Meta:
        model = ConsignmentgoodsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentgoodsaddForm,self).__init__(*args, **kwargs)
        self.fields['cg_consignmentnumber'].empty_label = "--Select--"
        self.fields['cg_currency_type'].empty_label = "--Select--"
        self.fields['cg_lastmodifiedby'].empty_label = "--Select--"
        self.fields['cg_description'].queryset = Stock_type.objects.all()
