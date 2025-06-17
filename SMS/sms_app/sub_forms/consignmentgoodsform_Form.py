from django import forms
from ..models import ConsignmentgoodsInfo,Stock_type,ConsigneeInfo,ConsignerInfo


class ConsignmentgoodsaddForm(forms.ModelForm):

    class Meta:
        model = ConsignmentgoodsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentgoodsaddForm,self).__init__(*args, **kwargs)
        self.fields['cg_consignmentnumber'].empty_label = "--Select--"
        self.fields['cg_currency_type'].empty_label = "--Select--"
        self.fields['cg_lastmodifiedby'].empty_label = "--Select--"
        self.fields['cg_consigner'].empty_label = "--Select--"
        self.fields['cg_consignee'].empty_label = "--Select--"
        self.fields['cg_description'].empty_label = "--Select--"
        self.fields['cg_description'].queryset = Stock_type.objects.all()
        self.fields['cg_consigner'].queryset = ConsignerInfo.objects.all()
        self.fields['cg_consignee'].queryset = ConsigneeInfo.objects.all()