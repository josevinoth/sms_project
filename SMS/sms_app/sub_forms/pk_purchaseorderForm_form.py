from django import forms
from ..models import PkpurchaseorderInfo

class PkpurchaseorderForm(forms.ModelForm):

    class Meta:
        model = PkpurchaseorderInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkpurchaseorderForm,self).__init__(*args, **kwargs)
        self.fields['po_updated_by'].empty_label = "--Select--"
        self.fields['po_assessment_num'].empty_label = "--Select--"
        self.fields['po_customer_name'].empty_label = "--Select--"
        self.fields['po_status'].empty_label = "--Select--"
