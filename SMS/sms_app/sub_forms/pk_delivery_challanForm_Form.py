from django import forms
from ..models import Pkdeliverychallan

class DeliverychallanForm(forms.ModelForm):
    class Meta:
        model = Pkdeliverychallan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeliverychallanForm,self).__init__(*args, **kwargs)
        self.fields['dc_customer_name'].empty_label = "--Select--"
        self.fields['dc_assessment_num'].empty_label = "--Select--"
        self.fields['dc_customer_po'].empty_label = "--Select--"

