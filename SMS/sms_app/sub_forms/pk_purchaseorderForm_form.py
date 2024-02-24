from django import forms
from ..models import PkpurchaseorderInfo

class PkpurchaseorderForm(forms.ModelForm):

    class Meta:
        model = PkpurchaseorderInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkpurchaseorderForm,self).__init__(*args, **kwargs)
        self.fields['po_updated_by'].empty_label = "--Select--"
