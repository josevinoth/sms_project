from django import forms
from ..models import pk_stock_statusinfo,PkcostingInfo

class PkretrivalForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkretrivalForm,self).__init__(*args, **kwargs)
        self.fields['ct_stock_status'].empty_label = "--Select--"
        self.fields['ct_stock_status'].queryset = pk_stock_statusinfo.objects.filter(id__in=[2, 3])