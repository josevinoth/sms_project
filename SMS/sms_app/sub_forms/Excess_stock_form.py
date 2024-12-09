from django import forms
from ..models import pk_stock_statusinfo,PkcostingInfo

class PkExcessstockForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'